"""
Picto:Bit v2.0 - Comunicador con pictogramas
Lee el número que envía la micro:bit receptora por USB y muestra
el pictograma a pantalla completa con su audio.

Salir: tecla ESC
"""
import os
import serial
import serial.tools.list_ports
import pygame

# ============ CONFIGURACIÓN ============
PUERTO_SERIE = None    # None = buscar la micro:bit automáticamente. O pon, por ejemplo, 'COM3'
BAUD_RATE = 9600       # ¡Debe ser el mismo que en la micro:bit receptora!
TIEMPO_VISIBLE = 5     # Segundos que se ve el pictograma. 0 = se queda hasta que llegue otro

# Carpeta donde está este script (así encuentra img/ y snd/ aunque VS Code
# lo ejecute desde otra carpeta)
CARPETA = os.path.dirname(os.path.abspath(__file__))

# MISMO ORDEN que la lista 'mensajes' de la micro:bit receptora.
# número: (texto que se muestra si falta la imagen, nombre de los archivos)
# Archivos esperados: img/<nombre>.png  y  snd/<nombre>.wav
PICTOGRAMAS = {
    1:  ("jugar",           "jugar"),
    2:  ("desayunar",       "desayunar"),
    3:  ("ir al patio",     "ir_al_patio"),
    4:  ("ir al colegio",   "ir_al_colegio"),
    5:  ("ir a casa",       "ir_a_casa"),
    6:  ("beber agua",      "beber_agua"),
    7:  ("dibujar",         "dibujar"),
    8:  ("recortar",        "recortar"),
    9:  ("comer",           "comer"),
    10: ("hacer un puzzle", "hacer_puzzle"),
    11: ("escuchar música", "escuchar_musica"),
    12: ("pegar",           "pegar"),
    13: ("tablet",          "tablet"),
    14: ("trabajar",        "trabajar"),
    15: ("ir al baño",      "ir_al_bano"),
}

BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (170, 170, 170)


# ============ CONEXIÓN CON LA MICRO:BIT ============
def buscar_puerto():
    """Busca el puerto de la micro:bit por su identificador USB."""
    if PUERTO_SERIE:
        return PUERTO_SERIE
    for p in serial.tools.list_ports.comports():
        if p.vid == 0x0D28:  # identificador USB de todas las micro:bit
            return p.device
    return None


def conectar():
    puerto = buscar_puerto()
    if not puerto:
        return None
    try:
        conexion = serial.Serial(puerto, BAUD_RATE, timeout=0.1)
        conexion.reset_input_buffer()  # descartar datos viejos
        print(f"Conectado a la micro:bit en {puerto}")
        return conexion
    except serial.SerialException as e:
        print(f"No se pudo abrir {puerto}: {e}")
        return None


# ============ PANTALLA Y SONIDO ============
pygame.init()
try:
    pygame.mixer.init()
    hay_audio = True
except pygame.error:
    print("Aviso: no se ha encontrado salida de audio. Funcionará sin sonido.")
    hay_audio = False

pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Picto:Bit - Comunicador")
pygame.mouse.set_visible(False)
ancho, alto = pantalla.get_size()

fuente_grande = pygame.font.SysFont(None, alto // 5)
fuente_peque = pygame.font.SysFont(None, alto // 20)


def escalar_sin_deformar(img):
    """Ajusta la imagen a la pantalla manteniendo su proporción."""
    w, h = img.get_size()
    escala = min(ancho / w, alto / h)
    return pygame.transform.smoothscale(img, (int(w * escala), int(h * escala)))


# Cargar todo al arrancar (así se muestra al instante y avisa de lo que falta)
imagenes = {}
sonidos = {}
faltan = []
for num, (texto, _) in PICTOGRAMAS.items():
    nombre = str(num)  # archivos nombrados por número: img/1.png, snd/1.wav...
    ruta_img = os.path.join(CARPETA, "img", nombre + ".png")
    ruta_snd = os.path.join(CARPETA, "snd", nombre + ".wav")
    if os.path.exists(ruta_img):
        imagenes[num] = escalar_sin_deformar(pygame.image.load(ruta_img).convert_alpha())
    else:
        faltan.append(f"img/{nombre}.png")
    if hay_audio and os.path.exists(ruta_snd):
        sonidos[num] = pygame.mixer.Sound(ruta_snd)
    elif hay_audio:
        faltan.append(f"snd/{nombre}.wav")

# Imagen de bienvenida / espera (opcional): img/espera.png o img/espera.jpg
imagen_espera = None
for ext in (".png", ".jpg", ".jpeg"):
    ruta_espera = os.path.join(CARPETA, "img", "espera" + ext)
    if os.path.exists(ruta_espera):
        imagen_espera = escalar_sin_deformar(pygame.image.load(ruta_espera).convert_alpha())
        break

if faltan:
    print("Faltan estos archivos (se mostrará el texto en su lugar):")
    for f in faltan:
        print("   -", f)


def texto_centrado(texto, fuente, color, y=None):
    superficie = fuente.render(texto, True, color)
    rect = superficie.get_rect(center=(ancho // 2, y if y is not None else alto // 2))
    pantalla.blit(superficie, rect)


def pantalla_espera(conectado):
    pantalla.fill(BLANCO)
    if imagen_espera:
        pantalla.blit(imagen_espera, imagen_espera.get_rect(center=(ancho // 2, alto // 2)))
    if not conectado:
        texto_centrado("Buscando la micro:bit... (revisa el cable USB)",
                       fuente_peque, GRIS, alto - alto // 15)
    pygame.display.flip()


def mostrar_pictograma(num):
    texto, _ = PICTOGRAMAS[num]
    pantalla.fill(BLANCO)
    if num in imagenes:
        img = imagenes[num]
        pantalla.blit(img, img.get_rect(center=(ancho // 2, alto // 2)))
    else:
        texto_centrado(texto.upper(), fuente_grande, NEGRO)
    pygame.display.flip()
    if num in sonidos:
        pygame.mixer.stop()  # cortar el audio anterior si aún sonaba
        sonidos[num].play()
    print(f"Pictograma recibido: {num} ({texto})")


# ============ BUCLE PRINCIPAL ============
microbit = conectar()
pantalla_espera(microbit is not None)
print("Picto:Bit listo. Pulsa ESC para salir.")

reloj = pygame.time.Clock()
ocultar_en = 0          # momento en que volver a la pantalla blanca
proximo_intento = 0     # para reintentar la conexión si se desconecta
ejecutando = True

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT or (
            evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE
        ):
            ejecutando = False

    ahora = pygame.time.get_ticks()

    # Reconectar si no hay micro:bit (cada 2 segundos)
    if microbit is None:
        if ahora >= proximo_intento:
            microbit = conectar()
            proximo_intento = ahora + 2000
            if ocultar_en == 0:
                pantalla_espera(microbit is not None)
    else:
        try:
            while microbit.in_waiting > 0:
                linea = microbit.readline().decode("utf-8", errors="ignore").strip()
                if linea.isdigit() and int(linea) in PICTOGRAMAS:
                    mostrar_pictograma(int(linea))
                    ocultar_en = ahora + TIEMPO_VISIBLE * 1000 if TIEMPO_VISIBLE > 0 else 0
        except (serial.SerialException, OSError):
            print("Se ha desconectado la micro:bit. Reintentando...")
            try:
                microbit.close()
            except Exception:
                pass
            microbit = None

    # Volver a la pantalla blanca cuando pase el tiempo
    if ocultar_en and ahora >= ocultar_en:
        ocultar_en = 0
        pantalla_espera(microbit is not None)

    reloj.tick(30)  # 30 vueltas por segundo: no satura el ordenador

if microbit:
    microbit.close()
pygame.quit()

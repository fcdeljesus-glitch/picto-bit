# Picto:Bit · micro:bit RECEPTORA (junto al maestro, conectada al portátil por USB)
# MakeCode (vista Python) · https://makecode.microbit.org
# Proyecto compartido: https://makecode.microbit.org/S22039-08995-60773-61851
#
# Extensión necesaria: OLED12864_I2C (buscar "oled12864").

idRecibido = 0
ultimoID = 0
tiempoUltimo = 0

# 1. RECEPCIÓN SÚPER RÁPIDA (solo guarda el número)
def on_received_number(receivedNumber):
    global idRecibido
    idRecibido = receivedNumber
radio.on_received_number(on_received_number)

# --- CONFIGURACIÓN INICIAL ---
radio.set_group(110)
serial.redirect_to_usb()
serial.set_baud_rate(BaudRate.BAUD_RATE9600)   # debe coincidir con BAUD_RATE de picto_bit.py
OLED12864_I2C.init(60)
OLED12864_I2C.show_string(0, 0, "Listo", 1)
basic.show_icon(IconNames.YES)

# Mismo orden que las tarjetas aprendidas por la cámara y que pc/img/1.png ... 15.png
mensajes = ["",
    "jugar",
    "desayunar",
    "ir al patio",
    "ir al colegio",
    "ir a casa",
    "beber agua",
    "dibujar",
    "recortar",
    "comer",
    "hacer un puzzle",
    "escuchar musica",
    "pegar",
    "tablet",
    "trabajar",
    "ir al bano"]

# 2. DIBUJADO EN EL BUCLE PRINCIPAL
def on_forever():
    global idRecibido, ultimoID, tiempoUltimo
    if idRecibido > 0:
        # A. Copiamos el número y vaciamos al momento (así no se pierde el siguiente)
        numero = idRecibido
        idRecibido = 0
        # B. Ignoramos las copias repetidas que manda la emisora
        esRepetido = numero == ultimoID and input.running_time() - tiempoUltimo < 2000
        if not esRepetido:
            ultimoID = numero
            tiempoUltimo = input.running_time()
            # C. Enviamos el número al PC
            serial.write_line(convert_to_text(numero))
            # D. Texto en la OLED
            OLED12864_I2C.clear()
            if numero >= 1 and numero <= 15:
                OLED12864_I2C.show_string(0, 0, mensajes[numero], 1)
            else:
                OLED12864_I2C.show_number(0, 0, numero, 1)
            # E. Chivato en los LEDs (al final, porque es lento)
            basic.show_number(numero)
    basic.pause(50)
basic.forever(on_forever)

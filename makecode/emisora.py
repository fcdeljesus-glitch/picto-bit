# Picto:Bit · micro:bit EMISORA (la lleva el alumno)
# MakeCode (vista Python) · https://makecode.microbit.org
# Proyecto compartido: https://makecode.microbit.org/S94147-16441-13294-82944
#
# Extensión necesaria: la de HuskyLens (bloques "huskylens2").
# La HuskyLens debe estar en protocolo I2C y en modo Reconocimiento de etiquetas.

tagID = 0
ultimoID = 0
ultimoEnvio = 0

# Dar tiempo a que la HuskyLens arranque antes de conectarla
basic.show_icon(IconNames.DIAMOND)
basic.pause(3000)
huskylens2.i2c_init()
huskylens2.switch_algorithm(huskylens2.Algorithm.ALGORITHM_TAG_RECOGNITION)
radio.set_group(110)          # mismo grupo en emisora y receptora
radio.set_transmit_power(7)   # potencia máxima
basic.clear_screen()

def enviar(numero: number):
    # Se envía 3 veces por si se pierde algún mensaje
    for i in range(3):
        radio.send_number(numero)
        basic.pause(50)

def on_forever():
    global tagID, ultimoID, ultimoEnvio
    huskylens2.get_result_tag_recognition()
    if huskylens2.available_tag_recognition():
        tagID = parse_float(convert_to_text(huskylens2.cached_result_tag_property(1, huskylens2.BasePropertyContentId.ID)))
        if tagID >= 1 and tagID <= 15:
            # Solo enviar si es un pictograma nuevo o han pasado 5 s
            if tagID != ultimoID or input.running_time() - ultimoEnvio > 5000:
                enviar(tagID)
                ultimoID = tagID
                ultimoEnvio = input.running_time()
                basic.show_number(tagID)
                basic.show_icon(IconNames.YES)
                basic.pause(500)
                basic.clear_screen()
    else:
        # La tarjeta se ha retirado: permitir reenviar la misma después
        ultimoID = 0
    basic.pause(100)
basic.forever(on_forever)

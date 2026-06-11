import json
import cv2

def obtener_imagen_dni_desde_wallet(did, ruta_wallet="data/wallet/wallet_simulado.json"):
    """
    Simula la obtención de una imagen de DNI desde un wallet de identidad digital.
    """

    with open(ruta_wallet, "r") as f:
        wallet = json.load(f)

    if did not in wallet:
        raise ValueError("Identidad no encontrada en el wallet")

    ruta_imagen = wallet[did]["dni_image"]
    imagen = cv2.imread(ruta_imagen)

    if imagen is None:
        raise IOError("No se pudo cargar la imagen del DNI")

    return imagen
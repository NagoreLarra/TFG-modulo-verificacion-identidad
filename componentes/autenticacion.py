import json
import cv2
import os


def obtener_usuario_desde_wallet(did_usuario):
    ruta_wallet="data/wallet/wallet_simulado.json"

    with open(ruta_wallet, "r", encoding="utf-8") as f:
        wallet = json.load(f)

    if did_usuario not in wallet:
        raise ValueError("Identidad no encontrada en el wallet")

    return wallet[did_usuario]


def obtener_imagen_dni_desde_wallet(did_usuario, ruta_wallet="data/wallet/wallet_simulado.json"):
    """
    Obtiene la imagen del DNI asociada a una identidad desde un wallet simulado.

    Parámetros:
    - did_usuario: identificador de la identidad (string)
    - ruta_wallet: ruta al fichero wallet.json

    Devuelve:
    - imagen DNI en formato OpenCV (numpy array)

    Lanza excepción si hay errores.
    """

    # 1. Cargar wallet
    if not os.path.exists(ruta_wallet):
        raise FileNotFoundError("No se encuentra el fichero del wallet")

    with open(ruta_wallet, "r", encoding="utf-8") as f:
        wallet = json.load(f)

    # 2. Comprobar identidad
    if did_usuario not in wallet:
        raise ValueError("Identidad no encontrada en el wallet")

    # 3. Obtener ruta de la imagen
    ruta_imagen = wallet[did_usuario].get("biometria", {}).get("dni_image")

    if not ruta_imagen:
        raise ValueError("La identidad no tiene imagen de DNI asociada")

    if not os.path.exists(ruta_imagen):
        raise FileNotFoundError("No se encuentra la imagen del DNI")

    # 4. Cargar imagen
    imagen = cv2.imread(ruta_imagen)

    if imagen is None:
        raise IOError("Error al cargar la imagen del DNI")

    return imagen
    
def capturar_imagen_webcam(max_camaras=4):
    """
    Captura una imagen desde la webcam disponible.
    Devuelve la imagen (frame) o lanza excepción.
    """
    camara_id = None

    for i in range(max_camaras):
        cam = cv2.VideoCapture(i)
        ret, _ = cam.read()
        cam.release()
        print(f"Cámara {i}: ", "OK" if ret else "NO FUNCIONA")
        if ret:
            camara_id = i

    if camara_id is None:
        raise RuntimeError("No se encontró ninguna cámara disponible")

    camara = cv2.VideoCapture(camara_id)
    print("📷 Pulsa ENTER para capturar tu cara...")
    input()

    ret, frame = camara.read()
    camara.release()

    if not ret:
        raise RuntimeError("Error al capturar imagen")

    print("Imagen capturada correctamente")
    return frame

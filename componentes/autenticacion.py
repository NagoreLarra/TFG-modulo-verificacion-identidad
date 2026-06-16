import json
import os
import cv2


# ==========================================================
# CARGA DEL WALLET
# ==========================================================
def cargar_wallet(ruta_wallet="data/wallet/wallet_simulado.json"):
    """
    Carga el wallet simulado desde disco.
    """
    if not os.path.exists(ruta_wallet):
        raise FileNotFoundError("No se encuentra el fichero del wallet")

    try:
        with open(ruta_wallet, "r", encoding="utf-8") as f:
            wallet = json.load(f)
    except Exception as e:
        raise IOError(f"Error al cargar el wallet: {str(e)}")

    if not isinstance(wallet, dict):
        raise ValueError("El wallet no tiene un formato válido")

    return wallet


# ==========================================================
# OBTENER USUARIO DESDE LA WALLET
# ==========================================================
def obtener_usuario_desde_wallet(
    did_usuario,
    ruta_wallet="data/wallet/wallet_simulado.json"
):
    wallet = cargar_wallet(ruta_wallet)

    if did_usuario not in wallet:
        raise ValueError("Identidad no encontrada en el wallet")

    return wallet[did_usuario]


# ==========================================================
# OBTENER IMAGEN DE REFERENCIA DESDE LA WALLET
# ==========================================================
def obtener_imagen_dni_desde_wallet(
    did_usuario,
    ruta_wallet="data/wallet/wallet_simulado.json"
):
    usuario = obtener_usuario_desde_wallet(did_usuario, ruta_wallet)

    ruta_imagen = usuario.get("biometria", {}).get("dni_image")

    if not ruta_imagen:
        raise ValueError("La identidad no tiene imagen de DNI asociada")

    if not os.path.exists(ruta_imagen):
        raise FileNotFoundError("No se encuentra la imagen del DNI")

    imagen = cv2.imread(ruta_imagen)

    if imagen is None:
        raise IOError("Error al cargar la imagen del DNI")

    return imagen


# ==========================================================
# DETECCIÓN DE CÁMARA DISPONIBLE
# ==========================================================
def detectar_camara_disponible(max_camaras=4):
    camara_id = None

    for i in range(max_camaras):
        cam = cv2.VideoCapture(i)
        ret, _ = cam.read()
        cam.release()

        print(f"Cámara {i}: {'OK' if ret else 'NO FUNCIONA'}")

        if ret and camara_id is None:
            camara_id = i

    if camara_id is None:
        raise RuntimeError("No se encontró ninguna cámara disponible")

    return camara_id


# ==========================================================
# CAPTURA DE IMAGEN DESDE WEBCAM
# ==========================================================
def capturar_imagen_webcam(max_camaras=4, pausa_manual=True):
    camara_id = detectar_camara_disponible(max_camaras=max_camaras)

    camara = cv2.VideoCapture(camara_id)

    if not camara.isOpened():
        raise RuntimeError("No se pudo abrir la cámara seleccionada")

    try:
        if pausa_manual:
            print("📷 Pulsa ENTER para capturar tu cara...")
            input()

        ret, frame = camara.read()

        if not ret or frame is None:
            raise RuntimeError("Error al capturar imagen desde la webcam")

    finally:
        camara.release()

    print("Imagen capturada correctamente")
    return frame


# ==========================================================
# VALIDACIÓN ESTRUCTURAL DEL WALLET
# ==========================================================
def validar_estructura_wallet(ruta_wallet="data/wallet/wallet_simulado.json"):
    wallet = cargar_wallet(ruta_wallet)

    for did, data in wallet.items():
        if "identidad" not in data:
            raise ValueError(f"{did}: falta bloque 'identidad'")

        if "documento" not in data:
            raise ValueError(f"{did}: falta bloque 'documento'")

        if "biometria" not in data:
            raise ValueError(f"{did}: falta bloque 'biometria'")

        if "dni_image" not in data["biometria"]:
            raise ValueError(f"{did}: falta 'dni_image' en biometría")

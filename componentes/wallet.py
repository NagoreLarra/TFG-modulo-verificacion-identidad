import json
import os
import cv2


# ==========================================================
# OBTENER USUARIO DESDE WALLET
# ==========================================================
def obtener_usuario_desde_wallet(did_usuario, ruta_wallet="data/wallet/wallet_simulado.json"):
    """
    Recupera los datos de identidad de un usuario desde la wallet simulada.

    Parámetros:
    - did_usuario: identificador descentralizado (string)
    - ruta_wallet: ruta al fichero JSON

    Devuelve:
    - diccionario con los datos del usuario

    Lanza excepción en caso de error.
    """

    # 1. Verificar existencia del wallet
    if not os.path.exists(ruta_wallet):
        raise FileNotFoundError("No se encuentra el fichero del wallet")

    # 2. Cargar wallet
    try:
        with open(ruta_wallet, "r", encoding="utf-8") as f:
            wallet = json.load(f)
    except Exception as e:
        raise IOError(f"Error al cargar el wallet: {str(e)}")

    # 3. Validar identidad
    if did_usuario not in wallet:
        raise ValueError("Identidad no encontrada en el wallet")

    return wallet[did_usuario]


# ==========================================================
# OBTENER IMAGEN DE REFERENCIA (DNI) DESDE WALLET
# ==========================================================
def obtener_imagen_dni_desde_wallet(
    did_usuario,
    ruta_wallet="data/wallet/wallet_simulado.json"
):
    """
    Obtiene la imagen del DNI asociada a una identidad desde la wallet.

    Esta imagen se utiliza exclusivamente como referencia para
    verificación biométrica durante la simulación.

    IMPORTANTE:
    - No persiste la imagen
    - Su uso es puntual (principio de minimización de datos)

    Parámetros:
    - did_usuario: identificador de usuario
    - ruta_wallet: ruta al JSON del wallet

    Devuelve:
    - imagen en formato OpenCV (numpy array)

    Lanza excepción en caso de error.
    """

    # 1. Obtener identidad completa
    usuario = obtener_usuario_desde_wallet(did_usuario, ruta_wallet)

    # 2. Obtener ruta de la imagen de DNI
    ruta_imagen = (
        usuario.get("biometria", {})
               .get("dni_image")
    )

    if not ruta_imagen:
        raise ValueError("La identidad no tiene imagen de DNI asociada")

    # 3. Verificar existencia del fichero
    if not os.path.exists(ruta_imagen):
        raise FileNotFoundError("No se encuentra la imagen del DNI")

    # 4. Cargar imagen con OpenCV
    imagen = cv2.imread(ruta_imagen)

    if imagen is None:
        raise IOError("Error al cargar la imagen del DNI")

    return imagen


# ==========================================================
# VALIDACIÓN DE ESTRUCTURA DEL WALLET
# ==========================================================
def validar_estructura_wallet(ruta_wallet="data/wallet/wallet_simulado.json"):
    """
    Valida que el wallet tenga la estructura mínima esperada.

    Útil para detectar errores antes de ejecutar la simulación.
    """

    if not os.path.exists(ruta_wallet):
        raise FileNotFoundError("No se encuentra el fichero del wallet")

    with open(ruta_wallet, "r", encoding="utf-8") as f:
        wallet = json.load(f)

    for did, data in wallet.items():

        if "identidad" not in data:
            raise ValueError(f"{did}: falta bloque 'identidad'")

        if "documento" not in data:
            raise ValueError(f"{did}: falta bloque 'documento'")

        if "biometria" not in data:
            raise ValueError(f"{did}: falta bloque 'biometria'")

        if "dni_image" not in data["biometria"]:
            raise ValueError(f"{did}: falta 'dni_image' en biometría")


# ==========================================================
# FUNCIÓN AUXILIAR PARA DEBUG CONTROLADO (NO PRODUCCIÓN)
# ==========================================================
def guardar_imagen_debug(imagen, nombre_archivo):
    """
    Guarda una imagen SOLO para depuración.

    Esta función NO debe usarse en producción.
    """

    ruta = f"debug/{nombre_archivo}"

    os.makedirs("debug", exist_ok=True)

    cv2.imwrite(ruta, imagen)

    return ruta


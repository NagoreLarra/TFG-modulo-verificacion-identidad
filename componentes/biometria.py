import os
import cv2
import numpy as np


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================
RUTA_CASCADE_DEFECTO = "modelos/haarcascade_frontalface_default.xml"
RUTA_ARCFACE_DEFECTO = "modelos/arcface.onnx"

# Carga diferida del modelo deep learning
_arc_net = None


# ==========================================================
# UTILIDADES INTERNAS COMUNES
# ==========================================================
def cargar_cascade(ruta_cascade=RUTA_CASCADE_DEFECTO):
    """
    Carga el detector facial Haar Cascade.
    """
    if not os.path.exists(ruta_cascade):
        raise FileNotFoundError("No se encuentra el fichero Haar Cascade")

    face_cascade = cv2.CascadeClassifier(ruta_cascade)

    if face_cascade.empty():
        raise IOError("No se pudo cargar el Haar Cascade")

    return face_cascade


def cargar_modelo_arcface(ruta_modelo=RUTA_ARCFACE_DEFECTO):
    """
    Carga el modelo ArcFace de forma diferida.
    """
    global _arc_net

    if _arc_net is None:
        if not os.path.exists(ruta_modelo):
            raise FileNotFoundError("No se encuentra el modelo ArcFace")

        try:
            _arc_net = cv2.dnn.readNetFromONNX(ruta_modelo)
        except Exception as e:
            raise IOError(f"No se pudo cargar el modelo ArcFace: {str(e)}")

    return _arc_net


def validar_imagen(imagen, nombre_variable="imagen"):
    """
    Valida que la imagen exista y tenga un formato compatible.
    """
    if imagen is None:
        raise ValueError(f"{nombre_variable} es None")

    if not isinstance(imagen, np.ndarray):
        raise TypeError(f"{nombre_variable} debe ser un numpy array")

    if len(imagen.shape) not in [2, 3]:
        raise ValueError(f"{nombre_variable} no tiene un formato de imagen válido")


def convertir_a_gris(imagen):
    """
    Convierte una imagen a escala de grises si es necesario.
    """
    if len(imagen.shape) == 2:
        return imagen

    return cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)


def detectar_rostro(imagen, face_cascade):
    """
    Detecta el rostro principal de una imagen y devuelve la región recortada.
    """
    validar_imagen(imagen, "imagen")

    gray = convertir_a_gris(imagen)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(80, 80)
    )

    if len(faces) == 0:
        return None

    # Seleccionar el rostro de mayor tamaño
    x, y, w, h = sorted(
        faces,
        key=lambda f: f[2] * f[3],
        reverse=True
    )[0]

    rostro = gray[y:y + h, x:x + w]

    return rostro


def normalizar_rostro(rostro, size=(200, 200)):
    """
    Normaliza el tamaño del rostro detectado.
    """
    if rostro is None:
        return None

    return cv2.resize(rostro, size)


# ==========================================================
# BIOMETRÍA TRADICIONAL (LBPH)
# ==========================================================
def evaluar_estado_lbph(confidence):
    """
    Interpreta la confianza devuelta por LBPH.

    En LBPH, valores más bajos implican mayor similitud.
    """
    if confidence <= 50:
        return "SATISFACTORIO"
    elif confidence <= 70:
        return "INCONCLUSO"
    else:
        return "RIESGO"


def resultado_anomalo_lbph():
    """
    Resultado estructurado para casos anómalos en LBPH.
    """
    return {
        "metodo": "LBPH",
        "metric_type": "lbph_confidence",
        "metric_value": None,
        "thresholds": {
            "match_fuerte": 50.0,
            "zona_gris": 70.0
        },
        "estado": "RESULTADO_ANOMALO"
    }


def verificar_biometria_tradicional(
    img_dni,
    img_camara,
    ruta_cascade=RUTA_CASCADE_DEFECTO
):
    """
    Verificación biométrica facial mediante LBPH.

    Este método se utiliza como biometría secundaria de contraste
    dentro de la simulación.
    """
    validar_imagen(img_dni, "img_dni")
    validar_imagen(img_camara, "img_camara")

    face_cascade = cargar_cascade(ruta_cascade)

    # 1. Detección facial
    rostro_dni = detectar_rostro(img_dni, face_cascade)
    rostro_camara = detectar_rostro(img_camara, face_cascade)

    if rostro_dni is None or rostro_camara is None:
        return resultado_anomalo_lbph()

    # 2. Normalización
    rostro_dni = normalizar_rostro(rostro_dni)
    rostro_camara = normalizar_rostro(rostro_camara)

    # 3. Verificar disponibilidad de OpenCV contrib
    if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
        raise RuntimeError(
            "La instalación de OpenCV no incluye el módulo cv2.face necesario para LBPH"
        )

    # 4. Crear reconocedor y entrenar
    try:
        reconocedor = cv2.face.LBPHFaceRecognizer_create()

        X_train = [rostro_dni]
        y_train = np.array([0])

        reconocedor.train(X_train, y_train)

        label, confidence = reconocedor.predict(rostro_camara)
    except Exception:
        return resultado_anomalo_lbph()

    # 5. Decisión
    estado = evaluar_estado_lbph(confidence)

    return {
        "metodo": "LBPH",
        "metric_type": "lbph_confidence",
        "metric_value": float(confidence),
        "thresholds": {
            "match_fuerte": 50.0,
            "zona_gris": 70.0
        },
        "estado": estado
    }


# ==========================================================
# BIOMETRÍA DEEP LEARNING (ARCFACE)
# ==========================================================
def resultado_anomalo_dl():
    """
    Resultado estructurado para casos anómalos en deep learning.
    """
    return {
        "metodo": "DeepLearning",
        "metric_type": "cosine_similarity",
        "metric_value": None,
        "thresholds": {
            "match_fuerte": 0.75,
            "zona_gris": 0.55
        },
        "estado": "RESULTADO_ANOMALO"
    }


def preparar_rostro_para_embedding(face_img):
    """
    Asegura que la imagen del rostro tenga 3 canales para el modelo deep learning.
    """
    if face_img is None:
        return None

    if len(face_img.shape) == 2:
        return cv2.cvtColor(face_img, cv2.COLOR_GRAY2BGR)

    if len(face_img.shape) == 3 and face_img.shape[2] == 1:
        return cv2.cvtColor(face_img, cv2.COLOR_GRAY2BGR)

    return face_img


def obtener_embedding(face_img, ruta_modelo=RUTA_ARCFACE_DEFECTO):
    """
    Obtiene el embedding facial normalizado a partir de una imagen de rostro.
    """
    if face_img is None:
        return None

    face_img = preparar_rostro_para_embedding(face_img)

    arc_net = cargar_modelo_arcface(ruta_modelo)

    try:
        blob = cv2.dnn.blobFromImage(
            face_img,
            scalefactor=1.0 / 128.0,
            size=(112, 112),
            mean=(127.5, 127.5, 127.5),
            swapRB=True,
            crop=False
        )

        arc_net.setInput(blob)
        emb = arc_net.forward().flatten()
    except Exception:
        return None

    norm = np.linalg.norm(emb)

    if norm < 1e-6:
        return None

    return emb / norm


def similitud_coseno(a, b):
    """
    Calcula similitud coseno entre dos embeddings normalizados.

    Cuanto más alto el valor, mayor similitud.
    """
    if a is None or b is None:
        return None

    return float(np.dot(a, b))


def evaluar_estado_deep_learning(similitud):
    """
    Interpreta la similitud coseno entre embeddings.

    Convención:
    - valores altos  -> mayor coincidencia
    - valores medios -> resultado incierto
    - valores bajos  -> mayor riesgo
    """
    if similitud >= 0.75:
        return "SATISFACTORIO"
    elif similitud >= 0.55:
        return "INCONCLUSO"
    else:
        return "RIESGO"


def verificar_biometria_deep_learning(
    img_dni,
    img_camara,
    ruta_cascade=RUTA_CASCADE_DEFECTO,
    ruta_modelo=RUTA_ARCFACE_DEFECTO
):
    """
    Verificación biométrica facial basada en deep learning (ArcFace).

    Este método constituye el mecanismo biométrico principal
    dentro de la simulación.
    """
    validar_imagen(img_dni, "img_dni")
    validar_imagen(img_camara, "img_camara")

    resultado = resultado_anomalo_dl()

    # 1. Detectar rostro
    face_cascade = cargar_cascade(ruta_cascade)

    rostro_ref = detectar_rostro(img_dni, face_cascade)
    rostro_live = detectar_rostro(img_camara, face_cascade)

    if rostro_ref is None or rostro_live is None:
        return resultado

    # 2. Normalizar
    rostro_ref = normalizar_rostro(rostro_ref)
    rostro_live = normalizar_rostro(rostro_live)

    # 3. Embeddings
    emb_ref = obtener_embedding(rostro_ref, ruta_modelo=ruta_modelo)
    emb_live = obtener_embedding(rostro_live, ruta_modelo=ruta_modelo)

    if emb_ref is None or emb_live is None:
        return resultado

    # 4. Similitud coseno
    sim = similitud_coseno(emb_ref, emb_live)

    if sim is None:
        return resultado

    # 5. Decisión
    estado = evaluar_estado_deep_learning(sim)

    resultado["metric_value"] = float(sim)
    resultado["estado"] = estado

    return resultado
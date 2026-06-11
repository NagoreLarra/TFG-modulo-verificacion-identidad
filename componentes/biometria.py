import cv2
import numpy as np

# ==================================================================================
# BIOMETRÍA UTILIZANDO ALGORITMOS TRADICIONALES
# ==================================================================================
# ---------------------------
# UTILIDADES INTERNAS
# ---------------------------

def detectar_rostro(imagen, face_cascade):
    gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(80, 80)
    )

    if len(faces) == 0:
        return None

    # Nos quedamos con el rostro más grande
    x, y, w, h = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
    rostro = gray[y:y+h, x:x+w]

    return rostro


def normalizar_rostro(rostro, size=(200, 200)):
    return cv2.resize(rostro, size)

def evaluar_estado_lbph(confidence):
    if confidence <= 50:
        return "MATCH_FUERTE"
    elif confidence <= 70:
        return "ZONA_GRIS"
    else:
        return "NO_MATCH"
        
def verificar_biometria_tradicional(
    img_dni,
    img_camara,
    ruta_cascade="modelos/haarcascade_frontalface_default.xml"
):
    """
    Verificación biométrica facial mediante LBPH (OpenCV clásico).
    """

    # 1. Cargar detector facial
    face_cascade = cv2.CascadeClassifier(ruta_cascade)
    if face_cascade.empty():
        raise IOError("No se pudo cargar el Haar Cascade")

    # 2. Detectar y normalizar rostros
    rostro_dni = detectar_rostro(img_dni, face_cascade)
    rostro_camara = detectar_rostro(img_camara, face_cascade)

    if rostro_dni is None or rostro_camara is None:
        return {
            "metodo": "LBPH",
            "metric_type": "lbph_confidence",
            "metric_value": None,
            "thresholds": {
                "match_fuerte": 50,
                "zona_gris": 70
            },
            "estado": "RESULTADO_ANOMALO"
        }

    rostro_dni = normalizar_rostro(rostro_dni)
    rostro_camara = normalizar_rostro(rostro_camara)

    # 3. Crear reconocedor LBPH
    reconocedor = cv2.face.LBPHFaceRecognizer_create()

    # Entrenamiento (simulación)
    X_train = [rostro_dni]
    y_train = [0]
    reconocedor.train(X_train, np.array(y_train))

    # 4. Predicción
    label, confidence = reconocedor.predict(rostro_camara)

    # 5. Decisión
    estado = evaluar_estado_lbph(confidence)

    return {
        "metodo": "LBPH",
        "metric_type": "lbph_confidence",
        "metric_value": float(confidence),
        "thresholds": {
            "match_fuerte": 50,
            "zona_gris": 70
        },
        "estado": estado
    }
# ==================================================================================
# BIOMETRÍA UTILIZANDO DEEP LEARNING
# ==================================================================================

# -------------------------
# MODELOS
# -------------------------
face_net = cv2.dnn.readNetFromTensorflow(
    "modelos/opencv_face_detector_uint8.pb",
    "modelos/opencv_face_detector.pbtxt"
)

arc_net = cv2.dnn.readNetFromONNX("modelos/arcface.onnx")

# eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
face_cascade = cv2.CascadeClassifier("modelos/haarcascade_frontalface_default.xml")

# -------------------------
# UTILIDADES
# -------------------------

def obtener_embedding(face_img):
    """
    Obtiene el embedding facial a partir de una imagen de rostro
    """

    if face_img is None:
        return None

    # ✅ Asegurar 3 canales
    if len(face_img.shape) == 2:
        # Imagen en escala de grises -> convertir a BGR
        face_img = cv2.cvtColor(face_img, cv2.COLOR_GRAY2BGR)

    if face_img.shape[2] == 1:
        face_img = cv2.cvtColor(face_img, cv2.COLOR_GRAY2BGR)

    # ✅ Crear blob
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

    # ✅ Normalización del embedding
    norm = np.linalg.norm(emb)
    if norm < 1e-6:
        return None

    return emb / norm

def similitud_coseno(a, b):
    return float(np.dot(a, b))

def verificar_biometria_deep_learning(
    img_dni, 
    img_camara,
    ruta_cascade="modelos/haarcascade_frontalface_default.xml"
):

    resultado = {
        "metodo": "DeepLearning",
        "metric_type": "cosine_distance",
        "metric_value": None,
        "thresholds": {
            "match_fuerte": 0.45,
            "zona_gris": 0.60
        },
        "estado": "RESULTADO_ANOMALO"
    }

    # 1️⃣ Detectar rostro
    face_cascade = cv2.CascadeClassifier(ruta_cascade)
    if face_cascade.empty():
        raise IOError("No se pudo cargar el Haar Cascade")

    rostro_ref = detectar_rostro(img_dni, face_cascade)
    rostro_live = detectar_rostro(img_camara, face_cascade)

    if rostro_ref is None or rostro_live is None:
        return resultado

    # 2️⃣ Normalizar
    rostro_ref = normalizar_rostro(rostro_ref)
    rostro_live = normalizar_rostro(rostro_live)

    # 3️⃣ Embeddings
    emb_ref = obtener_embedding(rostro_ref)
    emb_live = obtener_embedding(rostro_live)

    if emb_ref is None or emb_live is None:
        return resultado

    # 4️⃣ Similitud
    sim = similitud_coseno(emb_ref, emb_live)
    resultado["metric_value"] = float(sim)

    # 5️⃣ Decisión
    if sim <= 0.45:
        # resultado["estado"] = "MATCH_FUERTE"
        resultado["estado"] = "SATISFACTORIO"
    elif sim <= 0.60:
        # resultado["estado"] = "ZONA_GRIS"
        resultado["estado"] = "INCONCLUSO"
    else:
        # resultado["estado"] = "NO_MATCH"
        resultado["estado"] = "RIESGO"
    return resultado


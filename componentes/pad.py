import cv2
import numpy as np

# ==========================================================
# EVALUACIÓN PAD (PRESENTATION ATTACK DETECTION)
# ==========================================================
def evaluar_pad(
    img_camara,
    umbral_bonafide=100.0,
    umbral_zona_gris=60.0
):
    """
    Evaluación simplificada de PAD basada en nivel de enfoque
    (varianza del operador de Laplaciano).

    Este método permite una detección básica de posibles ataques
    de presentación (fotos, pantallas, imágenes borrosas).

    Clasificación:
    - bonafide  -> imagen nítida, probable captura real
    - zona_gris -> resultado incierto
    - ataque    -> posible intento de suplantación

    IMPORTANTE:
    - Es un enfoque simplificado (no detecta deepfakes)
    - Uso exclusivo en simulación técnica del TFG

    Parámetros:
    - img_camara: imagen capturada desde la webcam (numpy array)
    - umbral_bonafide: valor mínimo para considerar imagen válida
    - umbral_zona_gris: límite inferior de zona intermedia

    Devuelve:
    - diccionario estructurado con resultado PAD
    """

    # ==========================================================
    # VALIDACIONES DE ENTRADA
    # ==========================================================
    if img_camara is None:
        raise ValueError("La imagen de cámara es None")

    if not isinstance(img_camara, np.ndarray):
        raise TypeError("La imagen debe ser un numpy array")

    if len(img_camara.shape) not in [2, 3]:
        raise ValueError("Formato de imagen no válido")

    # ==========================================================
    # CONVERSIÓN A ESCALA DE GRISES
    # ==========================================================
    try:
        if len(img_camara.shape) == 3:
            gray = cv2.cvtColor(img_camara, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_camara
    except Exception as e:
        raise RuntimeError(f"Error al convertir imagen a gris: {str(e)}")

    # ==========================================================
    # CÁLCULO DE MÉTRICA (VARIANZA DEL LAPLACIANO)
    # ==========================================================
    try:
        var_laplaciano = cv2.Laplacian(gray, cv2.CV_64F).var()
    except Exception as e:
        raise RuntimeError(f"Error al calcular el Laplaciano: {str(e)}")

    # ==========================================================
    # DECISIÓN PAD
    # ==========================================================
    if var_laplaciano >= umbral_bonafide:
        estado = "bonafide"

    elif var_laplaciano >= umbral_zona_gris:
        estado = "zona_gris"

    else:
        estado = "ataque"

    # ==========================================================
    # RESULTADO ESTRUCTURADO
    # ==========================================================
    resultado = {
        "metodo": "PAD_blur",
        "descripcion_metodo": "Evaluación basada en nitidez (varianza Laplaciana)",
        "metric_type": "laplacian_variance",
        "metric_value": float(var_laplaciano),
        "thresholds": {
            "bonafide": float(umbral_bonafide),
            "zona_gris": float(umbral_zona_gris)
        },
        "estado": estado
    }

    return resultado
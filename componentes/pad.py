import cv2
import numpy as np


def evaluar_pad(
    img_camara,
    umbral_bonafide=100.0,
    umbral_zona_gris=60.0
):
    """
    Evaluación simple de PAD basada en nivel de enfoque (varianza del Laplaciano).

    Devuelve:
    - "bonafide"
    - "zona_gris"
    - "ataque"
    """

    # 1. Convertir a escala de grises
    gray = cv2.cvtColor(img_camara, cv2.COLOR_BGR2GRAY)

    # 2. Medida de enfoque (blur)
    var_laplaciano = cv2.Laplacian(gray, cv2.CV_64F).var()

    # 3. Decisión PAD
    if var_laplaciano >= umbral_bonafide:
        estado = "bonafide"
    elif var_laplaciano >= umbral_zona_gris:
        estado = "zona_gris"
    else:
        estado = "ataque"

    return {
        "metodo": "PAD_blur",
        "laplacian_var": float(var_laplaciano),
        "estado": estado
    }
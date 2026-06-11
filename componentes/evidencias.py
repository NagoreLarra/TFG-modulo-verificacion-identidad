# componentes/evidencias.py
import json
import os
from datetime import datetime, UTC

def generar_evidencia(
    usuario,
    resultados_tecnicos,
    ruta_log="data/evidencias/log.json"
):
    """
    Genera una evidencia mínima del proceso de verificación.

    - NO almacena imágenes
    - NO almacena biometría cruda
    """

    registro = {
        "usuario": usuario["atributos_presentados"]["nombre"],
        "dni": usuario["atributos_presentados"]["dni"],
        "resultados": resultados_tecnicos,
        "timestamp": datetime.now(UTC).isoformat()
    }

    os.makedirs(os.path.dirname(ruta_log), exist_ok=True)

    try:
        with open(ruta_log, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        logs = []

    logs.append(registro)

    with open(ruta_log, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)

    return registro




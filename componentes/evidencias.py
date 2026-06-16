import json
import os
from datetime import datetime, UTC


# ==========================================================
# GENERACIÓN DE EVIDENCIA ELECTRÓNICA
# ==========================================================
def generar_evidencia(
    usuario,
    sesion_verificacion,
    resultados_tecnicos,
    decision_final,
    motivo_decision=None,
    incidencia=None,
    revision_humana=None,
    notificacion_operador=None,
    decision_automatica=None,
    motivo_decision_automatica=None,
    ruta_log="data/evidencias/log.json"
):
    """
    Genera evidencia estructurada del proceso de verificación de identidad.

    La evidencia incluye:
    - Identidad verificada (mínima información)
    - Referencia a sesión y actuación judicial
    - Resultados técnicos obtenidos
    - Decisión final del sistema
    - Incidencias si las hubiera

    PRINCIPIOS:
    - NO se almacenan imágenes
    - NO se almacenan datos biométricos crudos
    - Cumple minimización de datos
    """

    # ==========================================================
    # VALIDACIONES DE ENTRADA
    # ==========================================================
    if sesion_verificacion is None:
        raise ValueError("La sesión de verificación es obligatoria")

    if resultados_tecnicos is None:
        raise ValueError("Los resultados técnicos son obligatorios")

    if decision_final is None:
        raise ValueError("La decisión final es obligatoria")

    # ==========================================================
    # DATOS DE USUARIO (MINIMIZADOS)
    # ==========================================================
    if usuario:
        nombre = usuario["atributos_presentados"].get("nombre")
        dni = usuario["atributos_presentados"].get("dni")
        did = usuario.get("did")
    else:
        nombre = None
        dni = None
        did = None

    # ==========================================================
    # CONSTRUCCIÓN DE LA EVIDENCIA
    # ==========================================================
    registro = {
        "session_id": sesion_verificacion.get("session_id"),
        "id_actuacion_judicial": sesion_verificacion.get("id_actuacion_judicial"),
        "organo_judicial": sesion_verificacion.get("organo_judicial"),

        "timestamp_inicio": sesion_verificacion.get("timestamp_inicio"),
        "timestamp_fin": datetime.now(UTC).isoformat(),

        "usuario": {
            "nombre": nombre,
            "dni": dni,
            "did": did
        },

        "decision_automatica": decision_automatica,
        "motivo_decision_automatica": motivo_decision_automatica,

        "decision_final": decision_final,
        "motivo_decision": motivo_decision,

        "resultados_tecnicos": resultados_tecnicos,

        "incidencia": incidencia,

        "notificacion_operador": notificacion_operador,
        "revision_humana": revision_humana
    }


    # ==========================================================
    # VALIDACIÓN DE RUTA
    # ==========================================================
    directorio = os.path.dirname(ruta_log)

    if directorio:
        os.makedirs(directorio, exist_ok=True)

    # ==========================================================
    # CARGAR LOG EXISTENTE
    # ==========================================================
    try:
        with open(ruta_log, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    # ==========================================================
    # AÑADIR NUEVA EVIDENCIA
    # ==========================================================
    logs.append(registro)

    # ==========================================================
    # GUARDAR LOG
    # ==========================================================
    try:
        with open(ruta_log, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)
    except Exception as e:
        raise IOError(f"No se pudo guardar la evidencia: {str(e)}")

    return registro


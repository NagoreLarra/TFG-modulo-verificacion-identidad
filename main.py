# import os
# import gc
# import uuid
# import cv2
# from datetime import datetime, UTC

# # IMPORTAR COMPONENTES
# from componentes.autenticacion import (
#     obtener_usuario_desde_wallet,
#     obtener_imagen_dni_desde_wallet,
#     capturar_imagen_webcam
# )

# from componentes.biometria import (
#     verificar_biometria_tradicional,
#     verificar_biometria_deep_learning
# )

# from componentes.pad import evaluar_pad
# from componentes.evidencias import generar_evidencia


# # ==========================================================
# # LIMPIEZA DE BIOMETRÍA
# # ==========================================================
# def limpiar_biometria_temporal(*imagenes):
#     for img in imagenes:
#         try:
#             del img
#         except:
#             pass
#     gc.collect()


# # ==========================================================
# # INICIALIZACIÓN SESIÓN
# # ==========================================================
# sesion_verificacion = {
#     "session_id": str(uuid.uuid4()),
#     "id_actuacion_judicial": "EJE-2026-0001",
#     "organo_judicial": "Juzgado_simulado_01",
#     "timestamp_inicio": datetime.now(UTC).isoformat(),
#     "estado_proceso": "INICIADO"
# }

# usuario = None
# img_dni = None
# img_camara = None
# decision_final = "PENDIENTE"
# motivo_decision = None
# incidencia = None

# resultado_lbph = {
#     "metodo": "LBPH",
#     "estado": "NO_EJECUTADO"
# }

# resultado_dl = {
#     "metodo": "DeepLearning",
#     "estado": "NO_EJECUTADO"
# }

# resultado_pad = {
#     "metodo": "PAD",
#     "estado": "NO_EJECUTADO"
# }
# try:
#     # ==========================================================
#     # FASE 1: CONSENTIMIENTO
#     # ==========================================================
#     consentimiento = True

#     if not consentimiento:
#         raise PermissionError("Sin consentimiento")

#     # ==========================================================
#     # FASE 2: IDENTIFICACIÓN
#     # ==========================================================
#     did_usuario = "did:example:8f3a9c2d"

#     # ==========================================================
#     # FASE 3: WALLET
#     # ==========================================================
#     usuario_wallet = obtener_usuario_desde_wallet(did_usuario)

#     # ==========================================================
#     # FASE 4: IMAGEN DNI
#     # ==========================================================
#     img_dni = obtener_imagen_dni_desde_wallet(did_usuario)

#     # ==========================================================
#     # FASE 5: CONTEXTO USUARIO
#     # ==========================================================
#     usuario = {
#         "did": did_usuario,
#         "atributos_presentados": {
#             "nombre": usuario_wallet["identidad"]["nombre"],
#             "dni": usuario_wallet["documento"]["numero"]
#         }
#     }

#     # ==========================================================
#     # FASE 6: CAPTURA WEBCAM
#     # ==========================================================
#     img_camara = capturar_imagen_webcam()

#     # ==========================================================
#     # DEBUG VISUAL (CLAVE PARA TU TFG)
#     # ==========================================================
#     print("Mostrando imágenes para validación visual...")

#     cv2.imshow("Imagen DNI (Referencia)", img_dni)
#     cv2.imshow("Imagen Cámara (Captura)", img_camara)

#     print("Pulsa cualquier tecla para continuar...")
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

#     # ==========================================================
#     # FASE 7: BIOMETRÍA
#     # ==========================================================
#     resultado_lbph = verificar_biometria_tradicional(img_dni, img_camara)
#     resultado_dl = verificar_biometria_deep_learning(img_dni, img_camara)

#     # ==========================================================
#     # FASE 8: PAD
#     # ==========================================================
#     resultado_pad = evaluar_pad(img_camara)

#     # ==========================================================
#     # FASE 9: DECISIÓN
#     # ==========================================================
#     if resultado_pad["estado"] != "bonafide":
#         decision_final = "REVISION_HUMANA"
#         motivo_decision = "PAD no válido"
#     else:
#         if resultado_dl["estado"] == "SATISFACTORIO":
#             decision_final = "VERIFICACION_POSITIVA"
#             motivo_decision = "Verificación correcta"
#         else:
#             decision_final = "REVISION_HUMANA"
#             motivo_decision = "Biometría no concluyente"

#     sesion_verificacion["estado_proceso"] = "FINALIZADO"

# except Exception as e:
#     incidencia = str(e)
#     decision_final = "REVISION_HUMANA"
#     # motivo_decision = "Error en ejecución"
#     motivo_decision = f"Error técnico: {str(e)}"
# finally:
#     # ==========================================================
#     # EVIDENCIA
#     # ==========================================================
#     evidencia = generar_evidencia(
#         usuario=usuario,
#         sesion_verificacion=sesion_verificacion,
#         resultados_tecnicos={
#             "lbph": resultado_lbph,
#             "dl": resultado_dl,
#             "pad": resultado_pad
#         },
#         decision_final=decision_final,
#         motivo_decision=motivo_decision,
#         incidencia=incidencia
#     )

#     # ==========================================================
#     # LIMPIEZA
#     # ==========================================================
#     limpiar_biometria_temporal(img_dni, img_camara)

#     # ==========================================================
#     # RESULTADOS
#     # ==========================================================
#     print("\n=== RESULTADO FINAL ===")
#     print("Decisión:", decision_final)
#     print("Motivo:", motivo_decision)
#     print("Evidencia:", evidencia)
import os
import gc
import uuid
import cv2
from datetime import datetime, UTC

# ==========================================================
# IMPORTAR COMPONENTES
# ==========================================================
from componentes.autenticacion import (
    obtener_usuario_desde_wallet,
    obtener_imagen_dni_desde_wallet,
    capturar_imagen_webcam
)

from componentes.biometria import (
    verificar_biometria_tradicional,
    verificar_biometria_deep_learning
)

from componentes.pad import evaluar_pad
from componentes.evidencias import generar_evidencia


# ==========================================================
# FUNCIÓN AUXILIAR DE LIMPIEZA DE DATOS BIOMÉTRICOS TEMPORALES
# ==========================================================
def limpiar_biometria_temporal(*imagenes, rutas_temporales=None):
    """
    Elimina referencias en memoria a imágenes biométricas y borra
    posibles ficheros temporales de depuración si existieran.
    """
    for img in imagenes:
        try:
            del img
        except Exception:
            pass

    if rutas_temporales:
        for ruta in rutas_temporales:
            try:
                if ruta and os.path.exists(ruta):
                    os.remove(ruta)
            except Exception:
                pass

    gc.collect()


# ==========================================================
# FUNCIÓN AUXILIAR DE NOTIFICACIÓN AL OPERADOR JURÍDICO
# ==========================================================
def notificar_operador_juridico(sesion_verificacion, usuario, motivo):
    """
    Simula la notificación al operador jurídico.
    En un entorno real sería email, sistema de gestión interno, etc.
    """
    nombre_usuario = (
        usuario["atributos_presentados"].get("nombre")
        if usuario and "atributos_presentados" in usuario
        else "NO_IDENTIFICADO"
    )

    notificacion = {
        "timestamp_notificacion": datetime.now(UTC).isoformat(),
        "destinatario": "operador_juridico_simulado_01",
        "canal": "sistema_interno_simulado",
        "motivo": motivo,
        "session_id": sesion_verificacion["session_id"],
        "usuario": nombre_usuario,
        "estado": "ENVIADA"
    }

    print("\n📢 NOTIFICACIÓN A OPERADOR JURÍDICO")
    print(f"Sesión: {sesion_verificacion['session_id']}")
    print(f"Usuario: {nombre_usuario}")
    print(f"Motivo: {motivo}")

    return notificacion


# ==========================================================
# FUNCIÓN AUXILIAR DE REVISIÓN HUMANA POR OPERADOR JURÍDICO
# ==========================================================
def revision_humana(usuario):
    """
    Simulación de revisión manual por operador jurídico.
    """
    print("\n👨‍⚖️ REVISIÓN MANUAL EN CURSO")

    # Simulación simple para TFG:
    # la decisión final la adopta el operador jurídico.
    decision_operador = "VERIFICACION_POSITIVA"

    resultado = {
        "decision_operador": decision_operador,
        "timestamp_revision": datetime.now(UTC).isoformat(),
        "operador": "operador_simulado_01",
        "observaciones": "Validación visual satisfactoria"
    }

    print(f"✅ Revisión manual completada: {decision_operador}")

    return resultado


# ==========================================================
# INICIALIZACIÓN DEL PROCESO Y ASOCIACIÓN A LA ACTUACIÓN
# ==========================================================
sesion_verificacion = {
    "session_id": str(uuid.uuid4()),
    "id_actuacion_judicial": "EJE-2026-0001",
    "organo_judicial": "Juzgado_simulado_01",
    "timestamp_inicio": datetime.now(UTC).isoformat(),
    "estado_proceso": "INICIADO"
}


# ==========================================================
# VARIABLES DE CONTROL DEL ORQUESTADOR
# ==========================================================
usuario = None
usuario_wallet = None
img_dni = None
img_camara = None
evidencia = None

resultado_lbph = {
    "metodo": "LBPH",
    "metric_type": "lbph_confidence",
    "metric_value": None,
    "thresholds": {
        "match_fuerte": 50,
        "zona_gris": 70
    },
    "estado": "NO_EJECUTADO"
}

resultado_dl = {
    "metodo": "DeepLearning",
    "metric_type": "cosine_similarity",
    "metric_value": None,
    "thresholds": {
        "match_fuerte": 0.75,
        "zona_gris": 0.55
    },
    "estado": "NO_EJECUTADO"
}

resultado_pad = {
    "metodo": "PAD_blur",
    "laplacian_var": None,
    "estado": "NO_EJECUTADO"
}

resultados_tecnicos = {
    "biometria_tradicional": resultado_lbph,
    "biometria_deeplearning": resultado_dl,
    "pad": resultado_pad
}

decision_final = "PENDIENTE"
motivo_decision = None
incidencia = None

resultado_revision_humana = None
notificacion_operador = None
decision_automatica = None
motivo_decision_automatica = None

# Si en algún momento generas ficheros temporales, añádelos aquí
rutas_temporales = []


try:
    # ==========================================================
    # FASE 1: PRESENTACIÓN DE IDENTIDAD Y CONSENTIMIENTO
    # ==========================================================
    presentacion = {
        "timestamp": datetime.now(UTC).isoformat(),
        "consentimiento_usuario": True,
        "metodo": "wallet_digital"
    }

    if not presentacion["consentimiento_usuario"]:
        decision_final = "CANCELADO_SIN_CONSENTIMIENTO"
        motivo_decision = (
            "El usuario no ha otorgado consentimiento para "
            "el tratamiento de datos biométricos."
        )
        sesion_verificacion["estado_proceso"] = "FINALIZADO_SIN_VERIFICACION"
        raise PermissionError(motivo_decision)

    # ==========================================================
    # FASE 2: IDENTIFICACIÓN PREVIA
    # ==========================================================
    did_usuario = "did:example:8f3a9c2d"

    # ==========================================================
    # FASE 3: RECUPERACIÓN DE ATRIBUTOS DESDE LA WALLET
    # ==========================================================
    usuario_wallet = obtener_usuario_desde_wallet(did_usuario)

    # ==========================================================
    # FASE 4: OBTENCIÓN DE IMAGEN DE REFERENCIA
    # ==========================================================
    img_dni = obtener_imagen_dni_desde_wallet(did_usuario)

    # ==========================================================
    # FASE 5: CONSTRUCCIÓN DEL CONTEXTO DE USUARIO
    # ==========================================================
    usuario = {
        "did": did_usuario,
        "rol": "interviniente",
        "origen": "wallet_simulado",
        "atributos_presentados": {
            "nombre": usuario_wallet["identidad"]["nombre"],
            "apellidos": usuario_wallet["identidad"]["apellidos"],
            "dni": usuario_wallet["documento"]["numero"]
        }
    }

    # ==========================================================
    # FASE 6: CAPTURA DE IMAGEN EN TIEMPO REAL
    # ==========================================================
    img_camara = capturar_imagen_webcam()

    # ==========================================================
    # DEBUG VISUAL
    # ==========================================================
    print("Mostrando imágenes para validación visual...")

    cv2.imshow("Imagen Cámara", img_camara)
    cv2.imshow("Imagen DNI", img_dni)

    print("Pulsa cualquier tecla para continuar...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # ==========================================================
    # FASE 7: VERIFICACIÓN BIOMÉTRICA
    # ==========================================================
    resultado_lbph = verificar_biometria_tradicional(
        img_dni,
        img_camara
    )

    resultado_dl = verificar_biometria_deep_learning(
        img_dni,
        img_camara
    )

    # ==========================================================
    # FASE 8: EVALUACIÓN PAD
    # ==========================================================
    resultado_pad = evaluar_pad(img_camara)
    estado_pad = resultado_pad["estado"]

    # ==========================================================
    # FASE 9: AGRUPACIÓN DE RESULTADOS TÉCNICOS
    # ==========================================================
    resultados_tecnicos = {
        "biometria_tradicional": resultado_lbph,
        "biometria_deeplearning": resultado_dl,
        "pad": resultado_pad
    }

    # ==========================================================
    # FASE 10: DECISIÓN FINAL AUTOMÁTICA DEL ORQUESTADOR
    # ==========================================================
    # Regla jerárquica:
    # 1. El PAD tiene prioridad absoluta.
    # 2. Si PAD es válido, manda el modelo principal DL.
    # 3. Casos anómalos o ambiguos => revisión humana.

    if estado_pad != "bonafide":
        decision_final = "REVISION_HUMANA"
        motivo_decision = (
            "El módulo PAD no ha clasificado la captura como bonafide."
        )

    else:
        estado_biometria = resultado_dl["estado"]

        if estado_biometria == "SATISFACTORIO":
            decision_final = "VERIFICACION_POSITIVA"
            motivo_decision = (
                "PAD válido y biometría principal satisfactoria."
            )

        elif estado_biometria in ["INCONCLUSO", "RIESGO", "RESULTADO_ANOMALO"]:
            decision_final = "REVISION_HUMANA"
            motivo_decision = (
                "Resultado biométrico no concluyente, de riesgo o anómalo."
            )

        else:
            decision_final = "REVISION_HUMANA"
            motivo_decision = (
                "Estado biométrico no reconocido por el orquestador."
            )

    sesion_verificacion["estado_proceso"] = "FINALIZADO"

except PermissionError as e:
    incidencia = {
        "tipo": "CONSENTIMIENTO",
        "detalle": str(e)
    }
    if decision_final == "PENDIENTE":
        decision_final = "CANCELADO_SIN_CONSENTIMIENTO"
    if motivo_decision is None:
        motivo_decision = str(e)

except (FileNotFoundError, ValueError, IOError) as e:
    incidencia = {
        "tipo": "ERROR_TECNICO_CONTROLADO",
        "detalle": str(e)
    }
    decision_final = "REVISION_HUMANA"
    motivo_decision = (
        "Incidencia técnica controlada durante la recuperación "
        "de identidad o biometría."
    )
    sesion_verificacion["estado_proceso"] = "FINALIZADO_CON_INCIDENCIA"

except RuntimeError as e:
    incidencia = {
        "tipo": "ERROR_OPERATIVO",
        "detalle": str(e)
    }
    decision_final = "REVISION_HUMANA"
    motivo_decision = (
        "Incidencia operativa durante la captura o ejecución del flujo."
    )
    sesion_verificacion["estado_proceso"] = "FINALIZADO_CON_INCIDENCIA"

except Exception as e:
    incidencia = {
        "tipo": "ERROR_NO_CONTROLADO",
        "detalle": str(e)
    }
    decision_final = "REVISION_HUMANA"
    motivo_decision = (
        "Se ha producido una incidencia no controlada. "
        "El caso debe escalarse a revisión humana."
    )
    sesion_verificacion["estado_proceso"] = "FINALIZADO_CON_INCIDENCIA"

finally:
    # ==========================================================
    # FASE 11: REVISIÓN HUMANA (SI APLICA)
    # ==========================================================
    if decision_final == "REVISION_HUMANA":
        decision_automatica = decision_final
        motivo_decision_automatica = motivo_decision

        notificacion_operador = notificar_operador_juridico(
            sesion_verificacion,
            usuario,
            motivo_decision
        )

        resultado_revision_humana = revision_humana(usuario)

        # La decisión final pasa a ser la del operador jurídico
        decision_final = resultado_revision_humana["decision_operador"]
        motivo_decision = "Decisión final validada por operador jurídico"

        sesion_verificacion["estado_proceso"] = "FINALIZADO_CON_REVISION_HUMANA"

    # ==========================================================
    # FASE 12: GENERACIÓN DE EVIDENCIA ELECTRÓNICA
    # ==========================================================
    evidencia = generar_evidencia(
        usuario=usuario,
        sesion_verificacion=sesion_verificacion,
        resultados_tecnicos=resultados_tecnicos,
        decision_final=decision_final,
        motivo_decision=motivo_decision,
        incidencia=incidencia,
        revision_humana=resultado_revision_humana,
        notificacion_operador=notificacion_operador,
        decision_automatica=decision_automatica,
        motivo_decision_automatica=motivo_decision_automatica
    )

    # ==========================================================
    # FASE 13: ELIMINACIÓN DE DATOS BIOMÉTRICOS TEMPORALES
    # ==========================================================
    limpiar_biometria_temporal(
        img_dni,
        img_camara,
        rutas_temporales=rutas_temporales
    )

    # ==========================================================
    # VISUALIZACIÓN DE RESULTADOS
    # ==========================================================
    print("\n=== RESULTADO FINAL ===")
    print("Decisión:", decision_final)
    print("Motivo:", motivo_decision)
    print("Evidencia:", evidencia)
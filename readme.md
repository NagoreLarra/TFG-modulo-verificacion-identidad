# TFG – Módulo de verificación de identidad

Este repositorio contiene el prototipo desarrollado como parte del Trabajo de Fin de Grado, cuyo objetivo es la simulación técnica de un módulo de verificación de identidad basado en visión por computador, integrado de forma desacoplada en un sistema de grabación de vistas.

El prototipo implementa un flujo completo de verificación orquestado, que abarca desde la presentación de identidad mediante cartera digital hasta la generación de evidencia electrónica del proceso.

El sistema emplea técnicas de:
- procesamiento de imagen
- biometría facial clásica (LBPH)
- verificación biométrica basada en aprendizaje profundo (ArcFace)

Además, incorpora un mecanismo simplificado de detección de ataques de presentación (PAD), que permite identificar intentos básicos de suplantación mediante análisis de calidad de imagen.

---

## Estructura del proyecto

- `componentes/`  
  Implementación de los distintos componentes funcionales del sistema:
  autenticación, biometría, detección de fraude (PAD) y generación de evidencias.

- `data/`  
  Datos simulados utilizados durante las pruebas (wallet e imágenes).

- `modelos/`  
  Carpeta destinada a los modelos de aprendizaje profundo, no incluida en el repositorio.

---

## Modelos de aprendizaje profundo

Los modelos necesarios para la verificación biométrica facial **no se incluyen en este repositorio**.

Esto se debe a que estos modelos (por ejemplo, ArcFace en formato ONNX o detectores faciales de OpenCV DNN) superan los límites de tamaño de Git y deben gestionarse externamente.

Para eje la carpeta 'modelos/'

**Nota:** Las rutas de los modelos se encuentran actualmente codificadas en el código fuente, por lo que cualquier cambio en la ubicación requerirá actualizar dichas rutas.cutar el prototipo, deben ubicarse en:
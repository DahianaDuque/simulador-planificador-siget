# Simulador de Planificador de CPU - SIGET

## Descripción

Simulador de planificación de procesos para el motor de procesamiento de datos del SIGET. El proyecto permite observar cómo diferentes algoritmos de planificación gestionan tareas relacionadas con movilidad urbana.

## Procesos simulados

El simulador trabaja con cuatro procesos:

- **P1 - Semáforos urbanos:** prioridad 3, 120 MB, 5 unidades de CPU.
- **P2 - Accidente vial:** prioridad 1, 40 MB, 3 unidades de CPU.
- **P3 - Flujo vehicular:** prioridad 4, 300 MB, 7 unidades de CPU.
- **P4 - Ambulancia prioritaria:** prioridad 2, 60 MB, 4 unidades de CPU.

En este modelo, el número 1 representa la prioridad más alta.

## Algoritmos implementados

### 1. Prioridad no expropiativa

Los procesos se ejecutan según su nivel de prioridad. Los procesos con prioridad más alta son seleccionados primero. Este algoritmo permite favorecer la atención de eventos críticos, como accidentes o ambulancias.

### 2. Round Robin

Se utiliza un quantum de **2 unidades de CPU**. Cada proceso recibe un intervalo de ejecución y, si no termina, vuelve a la cola de procesos listos. Esto permite distribuir el uso de la CPU de manera equitativa.

## Estados de los procesos

El simulador representa los siguientes estados:

**Nuevo → Listo → En ejecución → Bloqueado → Terminado**

En Round Robin también se puede observar el retorno de un proceso:

**En ejecución → Listo**

## Métricas

Para comparar el comportamiento de los algoritmos se calculan:

- Tiempo de espera.
- Tiempo de retorno.
- Tiempo de respuesta.
- Número de ejecuciones.
- Tiempo de respuesta promedio de las alertas críticas.

## Ejecución

Para ejecutar el simulador se necesita Python 3.

Desde la carpeta del proyecto ejecutar:

```bash
python simulador_siget.py

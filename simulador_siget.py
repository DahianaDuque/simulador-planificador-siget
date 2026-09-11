"""
Simulador de Planificador de CPU - SIGET
Algoritmos: Prioridad no expropiativa y Round Robin.
Estados: Nuevo, Listo, En ejecución, Bloqueado y Terminado.

Ejecutar:
    python simulador_siget.py
"""

from dataclasses import dataclass, field
from collections import deque
from typing import List, Dict, Tuple


@dataclass
class Proceso:
    pid: str
    nombre: str
    llegada: int
    prioridad: int          
    datos_mb: int
    rafaga: int            
    restante: int = field(init=False)
    estado: str = field(default="Nuevo", init=False)
    bloqueado_hasta: int = field(default=-1, init=False)
    inicio: int = field(default=-1, init=False)
    fin: int = field(default=-1, init=False)
    ejecuciones: int = field(default=0, init=False)

    def __post_init__(self):
        self.restante = self.rafaga


DATOS = [
    Proceso("P1", "Semáforos urbanos", llegada=0, prioridad=3, datos_mb=120, rafaga=5),
    Proceso("P2", "Accidente vial", llegada=1, prioridad=1, datos_mb=40, rafaga=3),
    Proceso("P3", "Flujo vehicular", llegada=2, prioridad=4, datos_mb=300, rafaga=7),
    Proceso("P4", "Ambulancia prioritaria", llegada=3, prioridad=2, datos_mb=60, rafaga=4),
]


def clonar_procesos() -> List[Proceso]:
    return [
        Proceso(p.pid, p.nombre, p.llegada, p.prioridad, p.datos_mb, p.rafaga)
        for p in DATOS
    ]


def registrar_estado(historial, tiempo, proceso, estado):
    historial.append((tiempo, proceso.pid if proceso else "-", estado))


def registrar_transicion(historial, tiempo, proceso, anterior, nuevo):
    historial.append((tiempo, proceso.pid, f"{anterior} -> {nuevo}"))


def liberar_bloqueados(procesos, tiempo):
    for p in procesos:
        if p.estado == "Bloqueado" and p.bloqueado_hasta <= tiempo:
            p.estado = "Listo"


def agregar_llegadas(procesos, tiempo, listos, historial):
    for p in procesos:
        if p.estado == "Nuevo" and p.llegada <= tiempo:
            anterior = p.estado
            p.estado = "Listo"
            listos.append(p)
            registrar_transicion(historial, tiempo, p, anterior, p.estado)


def calcular_metricas(procesos):
    for p in procesos:
        retorno = p.fin - p.llegada
        espera = retorno - p.rafaga
        respuesta = p.inicio - p.llegada
        p.metricas = (espera, retorno, respuesta)


def simular_prioridad(procesos):
    """Prioridad no expropiativa. Menor número = mayor prioridad."""
    tiempo = 0
    listos = []
    historial = []

    while any(p.fin < 0 for p in procesos):
        liberar_bloqueados(procesos, tiempo)
        agregar_llegadas(procesos, tiempo, listos, historial)

        if not listos:
            registrar_estado(historial, tiempo, None, "CPU libre")
            tiempo += 1
            continue

        listos.sort(key=lambda p: (p.prioridad, p.llegada))
        p = listos.pop(0)
        anterior = p.estado
        p.estado = "En ejecución"
        registrar_transicion(historial, tiempo, p, anterior, p.estado)
        if p.inicio < 0:
            p.inicio = tiempo

        for _ in range(p.restante):
            registrar_estado(historial, tiempo, p, "En ejecución")
            tiempo += 1
            p.restante -= 1

        p.ejecuciones += 1
        if p.fin < 0:
            anterior = p.estado
            p.estado = "Bloqueado"
            p.bloqueado_hasta = tiempo
            registrar_transicion(historial, tiempo, p, anterior, p.estado)
            tiempo += 1
            anterior = p.estado
            p.estado = "Terminado"
            p.fin = tiempo
            registrar_transicion(historial, tiempo, p, anterior, p.estado)

    calcular_metricas(procesos)
    return procesos, historial


def simular_round_robin(procesos, quantum=2):
    tiempo = 0
    cola = deque()
    historial = []

    while any(p.fin < 0 for p in procesos):
        liberar_bloqueados(procesos, tiempo)

        nuevas = sorted(
            [p for p in procesos if p.estado == "Nuevo" and p.llegada <= tiempo],
            key=lambda p: (p.llegada, p.pid)
        )
        for p in nuevas:
            p.estado = "Listo"
            cola.append(p)

        if not cola:
            registrar_estado(historial, tiempo, None, "CPU libre")
            tiempo += 1
            continue

        p = cola.popleft()
        if p.estado != "Listo":
            continue

        anterior = p.estado
        p.estado = "En ejecución"
        registrar_transicion(historial, tiempo, p, anterior, p.estado)
        if p.inicio < 0:
            p.inicio = tiempo

        pasos = min(quantum, p.restante)
        for _ in range(pasos):
            registrar_estado(historial, tiempo, p, "En ejecución")
            tiempo += 1
            p.restante -= 1

            nuevas = sorted(
                [x for x in procesos if x.estado == "Nuevo" and x.llegada <= tiempo],
                key=lambda x: (x.llegada, x.pid)
            )
            for x in nuevas:
                x.estado = "Listo"
                cola.append(x)

        p.ejecuciones += 1

        if p.restante == 0:
            p.estado = "Bloqueado"
            p.bloqueado_hasta = tiempo
            registrar_transicion(historial, tiempo, p, anterior, p.estado)
            tiempo += 1
            p.estado = "Terminado"
            p.fin = tiempo
            registrar_transicion(historial, tiempo, p, anterior, p.estado)
        else:
            anterior = p.estado
            p.estado = "Listo"
            registrar_transicion(historial, tiempo, p, anterior, p.estado)
            cola.append(p)

    calcular_metricas(procesos)
    return procesos, historial


def imprimir_resultado(titulo, procesos, historial):
    print("\n" + "=" * 78)
    print(titulo)
    print("=" * 78)

    print("\nLínea de tiempo (CPU):")
    ultimo = None
    inicio = None
    for t, pid, estado in historial:
        actual = pid if estado == "En ejecución" else "-"
        if actual != ultimo:
            if ultimo is not None:
                print(f"[{inicio:02d}-{t:02d}] {ultimo}")
            inicio = t
            ultimo = actual
    if ultimo is not None:
        print(f"[{inicio:02d}-{historial[-1][0] + 1:02d}] {ultimo}")

    print("\nEstados y transiciones (cronológicos):")
    print("Nuevo -> Listo -> En ejecución -> Bloqueado -> Terminado")
    for t, pid, estado in historial:
        if estado != "En ejecución":
            print(f"t={t:02d} | {pid:>2} | {estado}")

    print("\nMétricas:")
    print(f"{'PID':<5}{'Espera':<10}{'Retorno':<10}{'Respuesta':<12}{'Ejecuciones':<12}")
    for p in procesos:
        espera, retorno, respuesta = p.metricas
        print(f"{p.pid:<5}{espera:<10}{retorno:<10}{respuesta:<12}{p.ejecuciones:<12}")

    avg_espera = sum(p.metricas[0] for p in procesos) / len(procesos)
    avg_respuesta = sum(p.metricas[2] for p in procesos) / len(procesos)
    emergencias = [p for p in procesos if p.prioridad <= 2]
    avg_emergencia = sum(p.metricas[2] for p in emergencias) / len(emergencias)

    print(f"\nEspera promedio: {avg_espera:.2f}")
    print(f"Respuesta promedio: {avg_respuesta:.2f}")
    print(f"Respuesta promedio de alertas críticas: {avg_emergencia:.2f}")


def main():
    print("SIMULADOR DE PLANIFICADOR DE CPU - SIGET")
    print("1 = prioridad más alta. Los tiempos representan unidades de CPU.")

    prioridad, hist_p = simular_prioridad(clonar_procesos())
    rr, hist_rr = simular_round_robin(clonar_procesos(), quantum=2)

    imprimir_resultado("ALGORITMO 1: PRIORIDAD NO EXPROPIATIVA", prioridad, hist_p)
    imprimir_resultado("ALGORITMO 2: ROUND ROBIN (QUANTUM = 2)", rr, hist_rr)

    print("\nConclusión:")
    print("- Prioridad favorece la atención de incidentes críticos.")
    print("- Round Robin reparte el CPU de forma equitativa y evita monopolización.")
    print("- Para SIGET, una estrategia híbrida puede ser conveniente: prioridad para")
    print("  emergencias y Round Robin para tareas rutinarias de alto volumen.")


if __name__ == "__main__":
    main()

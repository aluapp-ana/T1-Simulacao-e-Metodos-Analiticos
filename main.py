"""
Rodar com:
    python3 main.py modeloT1.yml
"""

import sys

from carregador import carregar_modelo
from simulador_redes import SimuladorRede
from rede import RedeDeFilas
from fila import Fila

def formatar_resultado(fila):
    cap_str = "sem limite" if fila.capacity == float("inf") else str(fila.capacity)
    linhas = []
    linhas.append(f"--- {fila.nome} (indice {fila.indice}, G/G/{fila.Servers()}/{cap_str}) ---")
    if fila.tem_chegada_externa():
        linhas.append(f"Chegada externa: {fila.min_arrival} ... {fila.max_arrival}")
        if fila.tempo_primeira_chegada is not None:
            linhas.append(f"Primeiro cliente em: {fila.tempo_primeira_chegada}")
    linhas.append(f"Atendimento: {fila.min_service} ... {fila.max_service}")
    linhas.append(f"Roteamento: {fila.rotas}")
    linhas.append(f"{'Estado':<8}{'Tempo acumulado':<20}{'Probabilidade (%)':<20}")

    tempo_total = sum(fila.times.values())
    maior_estado = fila.capacity if fila.capacity != float("inf") else (max(fila.times.keys()) if fila.times else 0)
    for i in range(int(maior_estado) + 1):
        t = fila.times.get(i, 0.0)
        prob = (t / tempo_total) * 100 if tempo_total > 0 else 0.0
        linhas.append(f"{i:<8}{t:<20.4f}{prob:<20.4f}")

    linhas.append(f"Clientes perdidos: {fila.loss_count}")
    linhas.append("")
    return "\n".join(linhas)


def _clonar_rede(rede_modelo):
    novas_filas = []
    for fila in rede_modelo:
        nova = Fila(fila.nome, fila.server, fila.capacity,
                    fila.min_arrival, fila.max_arrival,
                    fila.min_service, fila.max_service,
                    fila.tempo_primeira_chegada, fila.rotas)
        novas_filas.append(nova)
    return RedeDeFilas(novas_filas)


def rodar_uma_vez(rede_modelo, limite_aleatorios, rng):
    rede_fresca = _clonar_rede(rede_modelo)
    sim = SimuladorRede(rede_fresca, limite_aleatorios=limite_aleatorios, rng=rng)
    tempo_global = sim.executar()
    return rede_fresca, tempo_global, sim.rng.contador


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else "modeloExemplo.yml"

    rede, limite_aleatorios, rng_ou_geradores = carregar_modelo(caminho)
    saida = [f"Simulacao de Rede de Filas - modelo: {caminho}", ""]

    if isinstance(rng_ou_geradores, list):
        for i, rng in enumerate(rng_ou_geradores, start=1):
            rede_rodada, tempo_global, consumidos = rodar_uma_vez(rede, limite_aleatorios, rng)
            saida.append(f"=== Rodada {i} (seed={rng.seed_inicial}) ===")
            saida.append(f"Numero de aleatorios consumidos: {consumidos}")
            saida.append(f"Tempo global de simulacao: {tempo_global:.4f}")
            saida.append("")
            for fila in rede_rodada:
                saida.append(formatar_resultado(fila))
    else:
        rede_rodada, tempo_global, consumidos = rodar_uma_vez(rede, limite_aleatorios, rng_ou_geradores)
        saida.append(f"Numero de aleatorios consumidos: {consumidos}")
        saida.append(f"Tempo global de simulacao: {tempo_global:.4f}")
        saida.append("")
        for fila in rede_rodada:
            saida.append(formatar_resultado(fila))

    texto_final = "\n".join(saida)
    print(texto_final)

    with open("resultado_simulacao.txt", "w") as f:
        f.write(texto_final)


if __name__ == "__main__":
    main()
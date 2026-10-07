"""
Rode com:

    python3 main.py [caminho para o modelo.yml]

Se nenhum caminho for passado, usa "modelo.yml" (a rede de 3 filas
do enunciado: Fila 1 roteando 20% para a Fila 2, 30% para a Fila 3 e 50%
para o exterior).
"""

import sys

from carregador import carregar_modelo
from simulador_redes import SimuladorRede


def formatar_resultado(fila):
    linhas = []
    linhas.append(f"--- {fila.nome} (indice {fila.indice}, G/G/{fila.Servers()}/{fila.Capacity()}) ---")
    if fila.tem_chegada_externa():
        linhas.append(f"Chegada externa: {fila.min_arrival} ... {fila.max_arrival}")
    linhas.append(f"Atendimento: {fila.min_service} ... {fila.max_service}")
    linhas.append(f"Roteamento: {fila.rotas}")
    linhas.append(f"{'Estado':<8}{'Tempo acumulado':<20}{'Probabilidade (%)':<20}")

    tempo_total = sum(fila.times)
    for i, t in enumerate(fila.times):
        prob = (t / tempo_total) * 100 if tempo_total > 0 else 0.0
        linhas.append(f"{i:<8}{t:<20.4f}{prob:<20.4f}")

    linhas.append(f"Clientes perdidos: {fila.loss_count}")
    linhas.append("")
    return "\n".join(linhas)


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else "modelo_exemplo.yml"

    rede, limite_aleatorios, rng = carregar_modelo(caminho)
    sim = SimuladorRede(rede, limite_aleatorios=limite_aleatorios, rng=rng)
    tempo_global = sim.executar()

    saida = []
    saida.append(f"Simulacao de Rede de Filas - modelo: {caminho}")
    saida.append(f"Numero de aleatorios consumidos: {sim.rng.contador}")
    saida.append(f"Tempo global de simulacao: {tempo_global:.4f}")
    saida.append("")
    for fila in rede:
        saida.append(formatar_resultado(fila))

    texto_final = "\n".join(saida)
    print(texto_final)

    with open("resultado_simulacao.txt", "w") as f:
        f.write(texto_final)


if __name__ == "__main__":
    main()
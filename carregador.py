"""
Carrega um modelo de rede de filas a partir de um arquivo .yml.

Formato esperado (ver `modelo.yml` para um exemplo completo):

simulacao:
  seed: 7                    # opcional -- semente do gerador pseudoaleatorio
  limite_aleatorios: 100000  # quantos aleatorios a simulacao deve consumir

filas:
  - nome: "Fila 1"
    servers: 1
    capacity: 3
    chegada:                 # OMITIR este bloco se a fila nao tem chegada externa
      min: 1
      max: 2
      primeiro_cliente: 1.0
    atendimento:
      min: 2
      max: 3
    roteamento:               # OMITIR = 100% para o exterior (padrao)
      - destino: 1             # indice (0-based) da fila na lista "filas" acima
        probabilidade: 0.2
      - destino: 2
        probabilidade: 0.3
      - destino: -1             # -1 = exterior (sai do sistema)
        probabilidade: 0.5

  - nome: "Fila 2"
    servers: 2
    capacity: 4
    atendimento:
      min: 3
      max: 5
    # sem "roteamento": vira automaticamente 100% para o exterior
"""

import yaml

from fila import Fila
from rede import RedeDeFilas
from gerador_pseudoaleatorio import Gerador


def carregar_modelo(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        dados = yaml.safe_load(f)

    config_sim = dados.get("simulacao", {}) or {}
    seed = config_sim.get("seed")
    limite_aleatorios = config_sim.get("limite_aleatorios", 100_000)

    lista_de_filas = []
    for item in dados["filas"]:
        chegada = item.get("chegada")
        atendimento = item["atendimento"]
        roteamento = item.get("roteamento") or [{"destino": -1, "probabilidade": 1.0}]

        fila = Fila(
            nome=item["nome"],
            servers=item["servers"],
            capacity=item["capacity"],
            min_arrival=chegada["min"] if chegada else None,
            max_arrival=chegada["max"] if chegada else None,
            min_service=atendimento["min"],
            max_service=atendimento["max"],
            tempo_primeira_chegada=chegada.get("primeiro_cliente") if chegada else None,
            rotas=[(r["destino"], r["probabilidade"]) for r in roteamento],
        )
        lista_de_filas.append(fila)

    rede = RedeDeFilas(lista_de_filas)
    rng = Gerador(seed=seed) if seed is not None else Gerador()
    return rede, limite_aleatorios, rng
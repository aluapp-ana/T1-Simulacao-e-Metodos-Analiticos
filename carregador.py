"""
Carrega um modelo de rede de filas a partir de um arquivo .yml no mesmo
estilo usado no simulador do professor (módulo 3):

!PARAMETERS
arrivals:
  Q1: 45.0

queues:
  Q1:
    servers: 1
    capacity: 5
    minArrival: 20.0
    maxArrival: 40.0
    minService: 10.0
    maxService: 12.0
  Q2:
    servers: 2
    capacity: 5
    minService: 30.0
    maxService: 120.0

network:
-  source: Q1
   target: Q2
   probability: 1.0

rndnumbers:        # OU "seeds" + "rndnumbersPerSeed" (ver abaixo)
- 0.2176
- 0.0103

Pontos de atenção do formato:

- `queues` é um MAPEAMENTO nome -> parametros (não uma lista). A ordem de
  declaração no arquivo vira o índice interno de cada fila (0, 1, 2...) --
  é por esse índice que o roteamento referencia as filas internamente.
- O roteamento não fica dentro de cada fila: é a lista separada
  `network`, com arestas `{source, target, probability}`. Se a soma das
  probabilidades que saem de uma fila for menor que 1.0, o restante vai
  implicitamente para o exterior (e se uma fila não aparece como `source`
  em nenhuma aresta, 100% dos clientes dela saem para o exterior).
- `arrivals` dá o tempo do PRIMEIRO cliente de cada fila que tem chegada
  externa (o intervalo de chegada em si continua em `minArrival`/
  `maxArrival`, dentro de `queues`). Só precisa aparecer para filas que
  têm chegada externa.
- `capacity` pode ser omitida -- nesse caso a fila fica sem limite de
  capacidade (nunca perde cliente por lotação).
- Números aleatórios, dois modos (se `seeds` estiver presente,
  `rndnumbers` é ignorado -- use só um dos dois no arquivo real):
    * `rndnumbers`: lista fixa de números -- reproduzidos exatamente,
      nesta ordem, via `GeradorLista`. É o modo certo para comparar
      resultado passo a passo com outro simulador que consome a mesma
      lista.
    * `seeds` + `rndnumbersPerSeed`: uma rodada por semente, cada uma
      consumindo `rndnumbersPerSeed` números do gerador LCG (`Gerador`)
      semeado com aquele valor.
"""

import yaml

from fila import Fila
from rede import RedeDeFilas
from gerador_pseudoaleatorio import Gerador, GeradorLista

def _remover_marcador_parametros(texto):
    """A primeira linha do arquivo costuma ser '!PARAMETERS', uma tag YAML
    sem conteúdo que o `yaml.safe_load` não aceita. Removemos essa linha
    (e qualquer outra igual a ela) antes do parse."""
    linhas = texto.splitlines()
    linhas_filtradas = [l for l in linhas if l.strip() != "!PARAMETERS"]
    return "\n".join(linhas_filtradas)

def carregar_modelo(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        texto = f.read()
        dados = yaml.safe_load(_remover_marcador_parametros(texto))

    nomes_filas = list(dados["queues"].keys())
    indice_por_nome = {nome: i for i, nome in enumerate(nomes_filas)}

    arestas_por_origem = {}
    for aresta in dados.get("network", []) or []:
        arestas_por_origem.setdefault(aresta["source"], []).append(aresta)

    arrivals = dados.get("arrivals", {}) or {}

    lista_de_filas = []
    for nome in nomes_filas:
        cfg = dados["queues"][nome]

        rotas = []
        soma = 0.0
        for aresta in arestas_por_origem.get(nome, []):
            rotas.append((indice_por_nome[aresta["target"]], aresta["probability"]))
            soma += aresta["probability"]
        if soma < 1.0 - 1e-9:
            rotas.append((-1, 1.0 - soma))
        if not rotas:
            rotas = [(-1, 1.0)]

        fila = Fila(
            nome=nome,
            servers=cfg["servers"],
            capacity=cfg.get("capacity"),  # None -> Fila trata como sem limite
            min_arrival=cfg.get("minArrival"),
            max_arrival=cfg.get("maxArrival"),
            min_service=cfg["minService"],
            max_service=cfg["maxService"],
            tempo_primeira_chegada=arrivals.get(nome),
            rotas=rotas,
        )
        lista_de_filas.append(fila)

    rede = RedeDeFilas(lista_de_filas)

    if "seeds" in dados:
        limite_por_semente = dados.get("rndnumbersPerSeed", 100_000)
        geradores = [Gerador(seed=s) for s in dados["seeds"]]
        return rede, limite_por_semente, geradores
    else:
        numeros = dados["rndnumbers"]
        return rede, len(numeros), GeradorLista(numeros)
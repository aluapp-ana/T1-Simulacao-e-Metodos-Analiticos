import yaml

from fila import Fila
from rede import RedeDeFilas
from gerador_pseudoaleatorio import Gerador, GeradorLista

def _remover_marcador_parametros(texto):
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
            capacity=cfg.get("capacity"),
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
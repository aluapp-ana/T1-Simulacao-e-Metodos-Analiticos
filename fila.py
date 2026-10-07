class Fila:
    """
    Propriedades: Server, Capacity, MinArrival, MaxArrival, MinService,
    MaxService, Customers, Loss, Times (tempo acumulado em cada estado).

    Para a rede genérica de "n" filas:

    - `indice`: posição desta fila dentro da listaDeFilas da rede. É
      preenchido automaticamente por RedeDeFilas (não precisa ser passado
      na mão) -- é esse índice que os eventos usam como FilaOrigem/
      FilaDestino.
    - `tempo_primeira_chegada`: só é usado se a fila tiver chegada externa
      (min_arrival/max_arrival definidos). None se a fila só recebe
      clientes de outras filas da rede.
    - `rotas`: lista de tuplas (indice_fila_destino, probabilidade).
      Use -1 no lugar do índice para "sai para o exterior" (a "fila
      imaginária" descrita no enunciado). As probabilidades de uma fila
      devem somar 1.0 -- inclusive quando há só uma rota (ex.: uma única
      fila final roteia 100% para -1).

      Exemplo (Fila 1 do modelo do módulo, roteando para a Fila 2 (índice
      1) com 20%, Fila 3 (índice 2) com 30% e exterior com 50%):
        rotas=[(1, 0.2), (2, 0.3), (-1, 0.5)]
    """

    def __init__(self, nome, servers, capacity,
                 min_arrival=None, max_arrival=None,
                 min_service=None, max_service=None,
                 tempo_primeira_chegada=None,
                 rotas=None):
        self.nome = nome
        self.server = servers
        self.capacity = capacity if capacity is not None else float("inf") # para filas com capacidade infinita
        self.min_arrival = min_arrival
        self.max_arrival = max_arrival
        self.min_service = min_service
        self.max_service = max_service
        self.tempo_primeira_chegada = tempo_primeira_chegada
        self.rotas = rotas if rotas is not None else [(-1, 1.0)]
        self.indice = None  # definido por RedeDeFilas ao montar a rede
        self.customers = 0
        self.loss_count = 0
        self.times = {}  # estado (int) -> tempo acumulado

    # ---- get/set conforme especificação do pseudocódigo ----
    def Status(self):
        return self.customers

    def Capacity(self):
        return self.capacity

    def Servers(self):
        return self.server

    def Loss(self):
        self.loss_count += 1

    def In(self):
        self.customers += 1

    def Out(self):
        self.customers -= 1

    def AcumulaEstado(self, delta_tempo):
        self.times[self.customers] = self.times.get(self.customers, 0.0) + delta_tempo

    def tem_chegada_externa(self):
        return self.min_arrival is not None and self.max_arrival is not None
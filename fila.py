class Fila:
    def __init__(self, nome, servers, capacity,
                 min_arrival=None, max_arrival=None,
                 min_service=None, max_service=None,
                 tempo_primeira_chegada=None,
                 rotas=None):
        self.nome = nome
        self.server = servers
        self.capacity = capacity if capacity is not None else float("inf")
        self.min_arrival = min_arrival
        self.max_arrival = max_arrival
        self.min_service = min_service
        self.max_service = max_service
        self.tempo_primeira_chegada = tempo_primeira_chegada
        self.rotas = rotas if rotas is not None else [(-1, 1.0)]
        self.indice = None
        self.customers = 0
        self.loss_count = 0
        self.times = {}

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
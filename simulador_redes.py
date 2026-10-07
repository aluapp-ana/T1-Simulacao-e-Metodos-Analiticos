from evento import Evento
from escalonador import Escalonador
from gerador_pseudoaleatorio import Gerador

EXTERIOR = -1

class SimuladorRede:
    def __init__(self, rede, limite_aleatorios, rng=None):
        self.rede = rede
        self.limite_aleatorios = limite_aleatorios
        self.rng = rng if rng is not None else Gerador()
        self.escalonador = Escalonador()
        self.relogio = 0.0

    def AcumulaTempo(self, tempo_evento):
        delta = tempo_evento - self.relogio
        for fila in self.rede:
            fila.AcumulaEstado(delta)
        self.relogio = tempo_evento

    def _sortear_destino(self, fila):
        rotas = fila.rotas
        if len(rotas) == 1:
            return rotas[0][0]

        r = self.rng.next()
        acumulado = 0.0
        for destino, prob in rotas:
            acumulado += prob
            if r < acumulado:
                return destino
        return rotas[-1][0]

    def ProcessaEvento(self, ev):
        self.AcumulaTempo(ev.tempo)

        # origem perde um cliente (se origem != exterior)
        if ev.origem != EXTERIOR:
            fila_origem = self.rede[ev.origem]
            fila_origem.Out()
            if fila_origem.Status() >= fila_origem.Servers():
                # ainda ha cliente esperando: o proximo comeca a ser atendido agora, e ja sorteamos seu destino final
                prox_destino = self._sortear_destino(fila_origem)
                t_servico = self.rng.uniforme(fila_origem.min_service, fila_origem.max_service)
                self.escalonador.Add(Evento(self.relogio + t_servico, ev.origem, prox_destino))

        # destino ganha um cliente (se destino != exterior)
        if ev.destino != EXTERIOR:
            fila_destino = self.rede[ev.destino]
            if fila_destino.Status() < fila_destino.Capacity():
                fila_destino.In()
                if fila_destino.Status() <= fila_destino.Servers():
                    prox_destino = self._sortear_destino(fila_destino)
                    t_servico = self.rng.uniforme(fila_destino.min_service, fila_destino.max_service)
                    self.escalonador.Add(Evento(self.relogio + t_servico, ev.destino, prox_destino))
            else:
                fila_destino.Loss()

        # se este evento era uma chegada externa, agenda a proxima
        if ev.origem == EXTERIOR:
            fila_chegada = self.rede[ev.destino]
            t_chegada = self.rng.uniforme(fila_chegada.min_arrival, fila_chegada.max_arrival)
            self.escalonador.Add(Evento(self.relogio + t_chegada, EXTERIOR, ev.destino))

    def CHEGADA(self, ev):
        self.ProcessaEvento(ev)

    def SAIDA(self, ev):
        self.ProcessaEvento(ev)

    def PASSAGEM(self, ev):
        self.ProcessaEvento(ev)

    def executar(self):
        for fila in self.rede:
            if fila.tem_chegada_externa():
                if fila.tempo_primeira_chegada is None:
                    raise ValueError(
                        f"Fila '{fila.nome}' tem chegada externa configurada, "
                        f"mas nenhum tempo_primeira_chegada foi definido"
                    )
                self.escalonador.Add(Evento(fila.tempo_primeira_chegada, EXTERIOR, fila.indice))

        while self.rng.contador < self.limite_aleatorios and not self.escalonador.vazio():
            ev = self.escalonador.ProximoEvento()
            if ev.tipo == "chegada":
                self.CHEGADA(ev)
            elif ev.tipo == "saida":
                self.SAIDA(ev)
            else:
                self.PASSAGEM(ev)

        return self.relogio
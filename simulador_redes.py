"""
Motor da simulação para uma rede de "n" filas com topologia genérica.

A ideia central pedida pelo módulo: CHEGADA, SAIDA e PASSAGEM deixam de
ser três procedimentos separados e viram UM SÓ (`ProcessaEvento`), porque
na prática os três fazem a mesma coisa -- "origem perde um cliente (se
existir origem), destino ganha um cliente (se existir destino)" -- e a
única diferença entre eles é se origem e/ou destino são reais ou o
"exterior" (índice -1):

  - chegada: origem = -1,            destino = indice de uma fila real
  - saida:   origem = indice real,   destino = -1
  - passagem: origem e destino são ambos índices reais

Quando uma fila libera o atendimento de um cliente (origem != -1), o
próximo destino desse mesmo "slot" de atendimento é sorteado pela tabela
de roteamento da fila de origem (`fila.rotas`), igual é feito quando um
cliente entra em atendimento em qualquer fila (destino != -1). Ou seja,
toda vez que um atendimento começa -- seja por chegada externa ou por
passagem de outra fila -- já se sorteia de uma vez qual vai ser o destino
do cliente quando esse atendimento terminar.
"""

from evento import Evento
from escalonador import Escalonador
from gerador_pseudoaleatorio import Gerador


EXTERIOR = -1


class SimuladorRede:
    """Motor de simulação de eventos discretos para uma rede de filas com
    topologia e roteamento genéricos (qualquer número de filas, qualquer
    tabela de roteamento entre elas, lida de um `RedeDeFilas`)."""

    def __init__(self, rede, limite_aleatorios, rng=None):
        self.rede = rede
        self.limite_aleatorios = limite_aleatorios
        self.rng = rng if rng is not None else Gerador()
        self.escalonador = Escalonador()
        self.relogio = 0.0

    def AcumulaTempo(self, tempo_evento):
        """Acumula o tempo decorrido no estado atual de TODAS as filas
        da rede, antes de processar o próximo evento."""
        delta = tempo_evento - self.relogio
        for fila in self.rede:
            fila.AcumulaEstado(delta)
        self.relogio = tempo_evento

    def _sortear_destino(self, fila):
        """ sorteia, pela tabela de roteamento da fila, o índice da próxima
        fila de destino (ou -1, exterior). Só consome um aleatório quando
        há mais de uma rota possível -- com uma única rota (prob. 1.0) o
        destino é certo e não deve gastar um número da sequência de
        aleatórios (senão o total de aleatórios consumidos na simulação
        não bateria mais com o valor-alvo do enunciado)."""
        rotas = fila.rotas
        if len(rotas) == 1:
            return rotas[0][0]

        r = self.rng.next()
        acumulado = 0.0
        for destino, prob in rotas:
            acumulado += prob
            if r < acumulado:
                return destino
        return rotas[-1][0]  # salvaguarda para arredondamento de ponto flutuante

    def ProcessaEvento(self, ev):
        """ implementação única e genérica: trata chegada, saída e
        passagem com o MESMO procedimento, porque os três sempre se
        resumem a 'origem perde um cliente (se existir origem)' seguido
        de 'destino ganha um cliente (se existir destino)'. CHEGADA,
        SAIDA e PASSAGEM (abaixo) só chamam este método -- eles existem
        apenas para dar nome ao que está acontecendo quando se lê o laço
        principal ou um log/print de depuração."""
        self.AcumulaTempo(ev.tempo)

        # ---- origem perde um cliente (se origem != exterior) ----
        if ev.origem != EXTERIOR:
            fila_origem = self.rede[ev.origem]
            fila_origem.Out()
            if fila_origem.Status() >= fila_origem.Servers():
                # ainda ha cliente esperando: o proximo comeca a ser
                # atendido agora, e ja sorteamos seu destino final
                prox_destino = self._sortear_destino(fila_origem)
                t_servico = self.rng.uniforme(fila_origem.min_service, fila_origem.max_service)
                self.escalonador.Add(Evento(self.relogio + t_servico, ev.origem, prox_destino))

        # ---- destino ganha um cliente (se destino != exterior) ----
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

        # ---- se este evento era uma chegada externa, agenda a proxima ----
        if ev.origem == EXTERIOR:
            fila_chegada = self.rede[ev.destino]
            t_chegada = self.rng.uniforme(fila_chegada.min_arrival, fila_chegada.max_arrival)
            self.escalonador.Add(Evento(self.relogio + t_chegada, EXTERIOR, ev.destino))

    # ---- atalhos nomeados: só delegam para ProcessaEvento. Existem para
    # que o restante do codigo (e quem le o executar() abaixo) continue
    # falando a mesma linguagem de CHEGADA/SAIDA/PASSAGEM dos modulos
    # anteriores, sem duplicar nenhuma logica. ----
    def CHEGADA(self, ev):
        """ev.origem == -1: um cliente chega de fora da rede."""
        self.ProcessaEvento(ev)

    def SAIDA(self, ev):
        """ev.destino == -1: um cliente termina o atendimento e sai da rede."""
        self.ProcessaEvento(ev)

    def PASSAGEM(self, ev):
        """origem e destino sao ambos filas reais: cliente é roteado de
        uma fila para outra dentro da rede."""
        self.ProcessaEvento(ev)

    def executar(self):
        """Agenda a primeira chegada de cada fila com chegada externa, e
        roda ate consumir `limite_aleatorios` numeros ou esvaziar o
        escalonador. Retorna o tempo global de simulacao."""
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
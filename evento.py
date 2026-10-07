class Evento:
    """
    Um evento agora carrega a fila de origem e a fila de destino (pelos
    seus índices na listaDeFilas da rede), em vez de um tipo fixo de
    "chegada"/"saida"/"passagem". Isso que permite generalizar o
    tratamento para qualquer topologia:

      - chegada externa: origem = -1, destino = indice da fila que recebe
      - saida para o exterior: origem = indice da fila, destino = -1
      - passagem entre filas: origem e destino são ambos índices válidos
        (inclusive podendo ser a mesma fila, se o modelo permitir isso)

    `tipo` é só um rótulo derivado para leitura/depuração -- a lógica do
    simulador nunca decide nada a partir dele, só de origem/destino.
    """

    def __init__(self, tempo, origem, destino):
        self.tempo = tempo
        self.origem = origem    # indice da fila de origem, ou -1 (exterior)
        self.destino = destino  # indice da fila de destino, ou -1 (exterior)

    def __lt__(self, other):
        return self.tempo < other.tempo

    @property
    def tipo(self):
        if self.origem == -1:
            return "chegada"
        if self.destino == -1:
            return "saida"
        return "passagem"

    def __repr__(self):
        return (f"Evento(tipo={self.tipo}, origem={self.origem}, "
                f"destino={self.destino}, tempo={self.tempo:.4f})")
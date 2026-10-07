class Evento:
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
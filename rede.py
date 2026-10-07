class RedeDeFilas:
    """ encapsula a listaDeFilas da rede como pedido no enunciado do MODULO 8 e valida o roteamento de cada fila: as
    probabilidades devem somar 1.0, e cada destino deve ser -1 (exterior)
    ou um índice válido dentro da lista.

    Preenche `fila.indice` automaticamente conforme a posição de cada
    fila na lista recebida, é por esse índice que os eventos (Evento)
    referenciam as filas.
    """

    EXTERIOR = -1

    def __init__(self, listaDeFilas):
        self.filas = list(listaDeFilas)
        for i, fila in enumerate(self.filas):
            fila.indice = i
        self._validar_rotas()

    def _validar_rotas(self):
        n = len(self.filas)
        for fila in self.filas:
            soma = sum(prob for _, prob in fila.rotas)
            if abs(soma - 1.0) > 1e-9:
                raise ValueError(
                    f"As probabilidades de roteamento de '{fila.nome}' "
                    f"(indice {fila.indice}) somam {soma}, mas deveriam somar 1.0"
                )
            for destino, _ in fila.rotas:
                if destino != self.EXTERIOR and not (0 <= destino < n):
                    raise ValueError(
                        f"Fila '{fila.nome}' roteia para o indice {destino}, "
                        f"que nao existe na rede (0..{n - 1}, ou -1 para exterior)"
                    )

    def __iter__(self):
        return iter(self.filas)

    def __len__(self):
        return len(self.filas)

    def __getitem__(self, indice):
        # Nunca deve ser chamado com indice == -1 (exterior); quem chama
        # (o motor da simulacao) ja filtra esse caso antes.
        return self.filas[indice]
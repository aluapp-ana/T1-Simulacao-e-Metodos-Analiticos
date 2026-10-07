class Gerador:
    # o sor tinha pedido pra aumentar o M, rodei o gerador antigo pra ver o grafico 
    # de dispersao e cheguei nesse valor, acho que ficou bom
    M = 2 ** 32 
    A = 1664525
    C = 1013904223
    X0 = 7

    def __init__(self, seed=None, a=None, c=None, m=None):
        self.a = a if a is not None else self.A
        self.c = c if c is not None else self.C
        self.m = m if m is not None else self.M
        self.x = seed if seed is not None else self.X0
        self.contador = 0  # quantos números já foram gerados

    def numeroNormalizado(self): # retorna proximo numero normalizado entre 0 e 1
        self.x = (self.a * self.x + self.c) % self.m
        self.contador += 1
        return self.x / self.m

    def uniforme(self, minimo, maximo): #sorteia um valor uniforme
        r = self.numeroNormalizado()
        return minimo + r * (maximo - minimo)


"""Gerador de números pseudoaleatórios (LCG) usado pela simulação.

Nome do arquivo sem acentuação de propósito: "gerador_pseudoaleatório.py"
(com acento) pode causar problema de encoding em alguns SOs/clientes git
(principalmente Windows), então padronizamos para "gerador_pseudoaleatorio.py".
Se seu código já importa pelo nome acentuado, só ajustar o import.
"""


class Gerador:
    """Gerador congruente linear misto: X_(n+1) = (a * X_n + c) mod m.

    M grande (ordem de bilhões) conforme o feedback já recebido sobre o
    simulador de fila única.
    """

    M_PADRAO = 2 ** 32          # ~4,29 bilhões
    A_PADRAO = 1664525
    C_PADRAO = 1013904223
    SEED_PADRAO = 7

    def __init__(self, seed=None, a=None, c=None, m=None):
        self.a = a if a is not None else self.A_PADRAO
        self.c = c if c is not None else self.C_PADRAO
        self.m = m if m is not None else self.M_PADRAO
        self.x = seed if seed is not None else self.SEED_PADRAO
        self.contador = 0  # quantos números já foram gerados

    def next(self):
        """Retorna o próximo número normalizado em [0, 1)."""
        self.x = (self.a * self.x + self.c) % self.m
        self.contador += 1
        return self.x / self.m

    def uniforme(self, minimo, maximo):
        """Sorteia um valor uniforme em [minimo, maximo]."""
        r = self.next()
        return minimo + r * (maximo - minimo)
"""Geradores de números pseudoaleatórios usados pela simulação.

- `Gerador`: LCG de verdade (gera os números).
- `GeradorLista`: "gerador" que só reproduz uma lista fixa de números já
  sorteados, na ordem dada -- usado para reproduzir, número por número, uma
  rodada específica (ex.: para comparar com outro simulador que consome a
  mesma lista de aleatórios, como no modo "rndnumbers" do formato do
  professor).

Nome do arquivo sem acentuação de propósito: "gerador_pseudoaleatório.py"
(com acento) pode causar problema de encoding em alguns SOs/clientes git
(principalmente Windows).
"""

class Gerador:
    """Gerador congruente linear misto: X_(n+1) = (a * X_n + c) mod m.

    M grande (ordem de bilhões) conforme o feedback já recebido sobre o
    simulador de fila única.
    """
    M = 2 ** 32 
    A = 1664525
    C = 1013904223
    X0 = 7

    def __init__(self, seed=None, a=None, c=None, m=None):
        self.seed_inicial = seed if seed is not None else self.X0
        self.a = a if a is not None else self.A
        self.c = c if c is not None else self.C
        self.m = m if m is not None else self.M
        self.x = self.seed_inicial
        self.contador = 0  # quantos números já foram gerados

    def next(self): # retorna proximo numero normalizado entre 0 e 1
        self.x = (self.a * self.x + self.c) % self.m
        self.contador += 1
        return self.x / self.m

    def uniforme(self, minimo, maximo): #sorteia um valor uniforme
        r = self.next()
        return minimo + r * (maximo - minimo)


class GeradorLista:
    """"Gerador" que consome, em ordem, uma lista já pronta de números em
    [0, 1) em vez de calcular via LCG. Útil para reproduzir exatamente a
    mesma sequência de aleatórios usada por outro simulador (ex.: o modo
    'rndnumbers' do formato do professor), permitindo comparar os
    resultados passo a passo sem depender do algoritmo gerador em si.
    """

    def __init__(self, numeros):
        self._numeros = list(numeros)
        self.seed_inicial = None
        self.contador = 0

    def next(self):
        if self.contador >= len(self._numeros):
            raise IndexError(
                f"Lista de aleatorios esgotada apos {self.contador} numeros"
            )
        r = self._numeros[self.contador]
        self.contador += 1
        return r

    def uniforme(self, minimo, maximo):
        r = self.next()
        return minimo + r * (maximo - minimo)
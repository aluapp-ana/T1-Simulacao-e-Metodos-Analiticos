class Gerador:
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
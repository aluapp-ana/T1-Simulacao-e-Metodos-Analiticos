import heapq


class Escalonador:
    def __init__(self):
        self._heap = []

    def Add(self, evento):
        heapq.heappush(self._heap, evento)

    def ProximoEvento(self):
        return heapq.heappop(self._heap)

    def vazio(self):
        return len(self._heap) == 0
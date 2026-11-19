# zewnetrzne
import copy
import numpy

# nasze
from graphs import AhoCorasick
from nodes import Node, bfs
from ownstring import Wzorzec

class Markov:
    @classmethod
    def zmacierzuj(cls, root: Node):
        """
        Każdy wierzchołek reprezentuje legalny stan, zatem każdy wiersz (kolumna) będzie reprezentować jeden stan.
        :param root: Wierzchołek grafu.
        :return: Gotowa macierz Markowa.
        """

        alphabet = {"A": 0.5, "B": 0.5}
        # todo zrobic zeby alfabet byl wstrzykiwany
        macierz =  numpy.empty((0, 0), dtype=float)

        with bfs(root) as search:
            def inner(node: Node):
                """
                Funkcja budująca częściowo macierz Markowa bez wykorzystania macierzy sąsiedztwa.

                :param node: wierzchołek w grafie
                :return: Nic. Funkcja zmienia zmienną macierz przy każdym wywołaniu.
                """

                nonlocal macierz

                i = search.visited[node]

                for char, pstwo in alphabet.items():
                    child = node[char]
                    if child is None:
                        child = root

                    j = search.visited[child]

                    n = len(search.visited)

                    if macierz.shape[0] < n:
                        expanded = numpy.zeros((n, n))
                        expanded[:macierz.shape[0], :macierz.shape[1]] = macierz
                        macierz = expanded

                    macierz[i, j] += pstwo

                return

            search.begin(inner)

        if numpy.any(macierz.sum(axis=1) != 1):
            raise ValueError(f"Wartości w wierszach macierzy powinny sumować się do 1.\n{macierz}")

        return macierz

    def __init__(self, *wzorce: Wzorzec):
        self.graf_niezdeterminowany = AhoCorasick(wzorce) # graf niezdeterminowany
        kopia = copy.deepcopy(self.graf_niezdeterminowany)
        # https://pl.wikipedia.org/wiki/Algorytm_Aho-Corasick#Determinizacja_automatu
        self.graf = AhoCorasick.determinize(kopia)
        self.macierz = self.zmacierzuj(self.graf)
        return
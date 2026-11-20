# zewnetrzne
import copy
from fractions import Fraction
import random

import numpy

# nasze
from graphs import AhoCorasick
from nodes import Node, bfs
from ownstring import Wzorzec
from traits import Alphabetizable, zalfabetyzuj


class Markov(Alphabetizable):
    @classmethod
    def zmacierzuj(cls, root: Node):
        """
        Każdy wierzchołek reprezentuje legalny stan, zatem każdy wiersz (kolumna) będzie reprezentować jeden stan.
        :param root: Wierzchołek grafu.
        :return: Gotowa macierz Markowa.
        """

        macierz =  numpy.empty((0, 0), dtype=object)

        with bfs(root) as search:
            def inner(node: Node):
                """
                Funkcja budująca częściowo macierz Markowa bez wykorzystania macierzy sąsiedztwa.

                :param node: wierzchołek w grafie
                :return: Nic. Funkcja zmienia zmienną macierz przy każdym wywołaniu.
                """

                nonlocal macierz

                i = search.visited[node]

                for char, pstwo in cls.alfabet.items():
                    child = node[char]
                    if child is None:
                        child = root

                    j = search.visited[child]

                    n = len(search.visited)

                    if macierz.shape[0] < n:
                        expanded = numpy.full((n, n), Fraction(0), dtype=object)
                        expanded[:macierz.shape[0], :macierz.shape[1]] = macierz
                        macierz = expanded

                    macierz[i, j] += pstwo

                return

            search.begin(inner)

        if numpy.any(macierz.sum(axis=1) != 1):
            raise ValueError(f"Wartości w wierszach macierzy powinny sumować się do 1.\n{macierz}")

        return macierz

    def wykonaj_krok(self):
        char, *_ = random.choices(
            population=list(self.alfabet.keys()),
            weights=list(self.alfabet.values()),
            k=1
        )

        self.current = self.current[char]

        return char

    def symuluj(self):
        napis = ""
        self.n = 0
        while not "".join(self.current.output) in self.wzorce:
            char = self.wykonaj_krok()
            napis += char
            self.n += 1

        return napis, "".join(self.current.output), self.n

    def __init__(self, *wzorce: Wzorzec):
        self.wzorce = wzorce

        zalfabetyzowany_aho_corasick = zalfabetyzuj(self.alfabet)(AhoCorasick)
        self.graf_niezdeterminowany = zalfabetyzowany_aho_corasick(wzorce) # graf niezdeterminowany

        kopia = copy.deepcopy(self.graf_niezdeterminowany)
        # https://pl.wikipedia.org/wiki/Algorytm_Aho-Corasick#Determinizacja_automatu
        self.graf = zalfabetyzowany_aho_corasick.determinize(kopia)

        self.macierz = self.zmacierzuj(self.graf)
        self.n = 0

        self.current = self.graf
        return
# zewnetrzne
import copy
from fractions import Fraction
import random
from functools import partial
from typing import Literal

import numpy
from matplotlib import pyplot as plt

# nasze
from graphs import AhoCorasick
from nodes import Node, bfs
from ownstring import Wzorzec
from traits import Alphabetizable, zalfabetyzuj, Drawable

class Macierz(numpy.ndarray, Drawable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.latex = ""
        return

    @classmethod
    def empty(cls, shape: tuple[int, ...], dtype: object = float, order: Literal["C", "F"] | None = "C"):
        return numpy.empty(shape, dtype=dtype, order=order).view(cls)

    @classmethod
    def full(cls, shape: tuple[int, ...], fill_value, dtype = None, order: Literal["C", "F"] | None = "C"):
        return numpy.full(
            shape, fill_value, dtype=dtype, order=order
        ).view(cls)

    def draw(self, filename: str = "matrix"):
        plt.rcParams["text.usetex"] = True
        plt.rcParams["text.latex.preamble"] = (
            r"\usepackage{amsmath}" "\n"
            fr"\setcounter{{MaxMatrixCols}}{{{self.shape[1]}}}"
        )

        self.latex = (
                r"\begin{bmatrix}"
                + r" \\ ".join(" & ".join(map(str, row)) for row in self)
                + r"\end{bmatrix}"
        )

        self.fig = plt.figure(figsize=(1, 1))
        self.fig.text(0.05, 0.5, f"${self.latex}$", fontsize=14)
        plt.axis("off")
        self.save = partial(self.fig.savefig, fname=f"{filename}.pdf")

        return self

    def render(self):
        self.save(bbox_inches="tight", pad_inches=0.1)
        plt.close(self.fig)
        self.fig = None

        return

class Markov(Alphabetizable):
    @classmethod
    def zmacierzuj(cls, root: Node) -> Macierz:
        """
        Każdy wierzchołek reprezentuje legalny stan, zatem każdy wiersz (kolumna) będzie reprezentować jeden stan.
        :param root: Wierzchołek grafu.
        :return: Gotowa macierz Markowa.
        """

        macierz = Macierz.empty((0, 0), dtype=object)

        with bfs(root) as search:
            def inner(node: Node):
                """
                Funkcja budująca częściowo macierz Markowa bez wykorzystania macierzy sąsiedztwa.

                :param node: Wierzchołek w grafie
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
                        expanded = Macierz.full((n, n), Fraction(0), dtype=object)
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
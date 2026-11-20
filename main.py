# zewnetrzne
from itertools import product
import numpy as np
import matplotlib.pyplot as plt
import sympy
from fractions import Fraction

# nasze
from generator import Generator
from markov import Markov
from common import Symbol

def main():

    # niech alfabet będzie bezprefiksowy i niech alfabet będzie miał tylko znaki, które są pojedynczymi tokenami
    # przykład kiedy alfabet nie jest bezprefiksowy ale da się zrobić dekoding: {0, 01, 11}
    # https://en.wikipedia.org/wiki/Sardinas%E2%80%93Patterson_algorithm
    n = Symbol("dlugosc")
    alfabet = {"A": Fraction(1, 2), "B": Fraction(1, 2)}
    with Generator(alfabet, (n == 3)) as gen:
        wzorzec1 = gen.Wzorzec("BAB")
        wzorzec2 = gen.Wzorzec("ABA")

        markov = gen.Markov(wzorzec1, wzorzec2)
        napis, rezultat, kroki = markov.symuluj()
        print(f"Napis: {napis}, Rezultat: {rezultat} w {kroki} krokach.")

        # markov.graf.draw("graf_zdeterminowany").render()
        # markov.graf_niezdeterminowany.draw("graf_niezdeterminowany").render()
        # print(markov.macierz)

        wzorce_dlugosci_trzy = [gen.Wzorzec(napis) for napis in ["".join(p) for p in product(alfabet, repeat=3)]]
        pary_wzorcow = [(napis1, napis2) for napis1, napis2 in product(wzorce_dlugosci_trzy, repeat=2) if napis1 != napis2]

        wyniki = []
        for napis1, napis2 in pary_wzorcow:
            wzorzec1 = gen.Wzorzec(napis1)
            wzorzec2 = gen.Wzorzec(napis2)
            parowy_markov = gen.Markov(wzorzec1, wzorzec2)
            wyniki.append((wzorzec1, wzorzec2, parowy_markov.symuluj()))



    return

main()
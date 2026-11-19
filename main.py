# zewnetrzne
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
    with Generator({"A": Fraction(1, 3), "B": Fraction(1, 3), "C": Fraction(1, 3)}, (n == 3)) as gen:
        wzorzec1 = gen.Wzorzec("AAB")
        wzorzec2 = gen.Wzorzec("AAA")

        markov = gen.Markov(wzorzec1, wzorzec2)
        markov.graf.draw("graf_zdeterminowany").render()
        print(markov.macierz)

    return

main()
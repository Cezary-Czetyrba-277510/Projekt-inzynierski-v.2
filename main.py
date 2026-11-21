# zewnetrzne
from itertools import product
from fractions import Fraction

# nasze
from generator import Generator
from common import Symbol

def main():

    # niech alfabet będzie bezprefiksowy i niech alfabet będzie miał tylko znaki, które są pojedynczymi tokenami
    # przykład, kiedy alfabet nie jest bezprefiksowy, ale da się zrobić dekoding: {0, 01, 11}
    # https://en.wikipedia.org/wiki/Sardinas%E2%80%93Patterson_algorithm
    n = Symbol("dlugosc")
    alfabet = {"A": Fraction(1, 2), "B": Fraction(1, 2)}
    with Generator(alfabet, (n == 3)) as gen:
        wzorzec1 = gen.Wzorzec("BAB")
        wzorzec2 = gen.Wzorzec("ABA")
        # Można rozszerzyć te wzorce, żeby nie były tylko literałami, ale też wyrażeniami regularnymi z lookbackiem.
        # To modelowałoby proces Markowa który "pamiętałby" od n-tego kroku k-kroków do tyłu.
        # Przykład:
        # wzorzec1 = gen.Wzorzec("B.{4}AAB")
        # wzorzec byłby listą napisów, które mają na początku B, 4 dowolne litery (z alfabetu) i na końcu AAB.
        # Wtedy każdy napis z tej listy byłby stanem końcowym.
        # W algorytmie konstrukcji przestrzeni stanów takie wyrażenie regularne byłoby prekomputowane do listy wszystkich możliwych
        # napisów spełniających warunek B na początku, 4 dowolne litery i AAB na końcu.
        # Można jeszcze skomplikować pisząc wzorzec, który ma na początku B, 2 miejsca do przodu nie ma A, 2 miejsca znowu do przodu mamy AAB
        # wzorzec 1 = gen.Wzorzec("B.{2}[^A].{2}AAB")
        # Albo pisać wzorce, które mają cały alfabet A-Z i jednocześnie te same warunki co wcześniej.
        # wzorzec1 = gen.Wzorzec("B.{2}[^ABC].{2}AAB")
        # wzorzec, który nie ma ani A, ani B, ani C na 6 miejscu od końca, ale ma dozwolone przynajmniej literki A, B, C
        # kropka to tzw. wildcard, który przepuści match bez względu na to, jaki znaczek tam występuje.
        # Zaimplementowany proces Markowa, który patrzy się k miejsc do tyłu, potrzebuje funkcji (najlepiej anonimowej),
        # która jest wywoływana w trakcie budowy macierzy Markowa.
        # Taka funkcja będzie budować prawdopodobieństwa warunkowe, które będą prawdopodobieństwami przejścia ze stanu i do stanu j.


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
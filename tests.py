# zewnetrzne
from fractions import Fraction
import unittest

import sympy

# nasze
from generator import Generator
from wyjatki import *
from common import Symbol

class TestOgranicz(unittest.TestCase):
    def test_suma_pstw(self):
        with self.assertRaises(ValueError):
            p1 = Fraction(1, 3)
            p2 = Fraction(1, 2)
            assert p1 + p2 != 1, "W teście sprawdzającym sumy prawdopodobieństw testowa suma prawdopodobieństw błędnie jest równa 1." # nie zmieniać

            alfabet = {"A": p1, "B": p2}
            napis = "AAB"
            assert all(char in alfabet for char in napis), "W teście sprawdzającym sumy prawdopodobieństw nie każdy znak w napisie składa się ze znaków alfabetu." # nie zmieniać

            with Generator(alfabet) as gen:
                wzorek = gen.Wzorzec(napis)

    def test_zle_znaczki(self):
        with self.assertRaises(ValueError):
            alfabet = {"A": Fraction(1,2), "B": Fraction(1,2)}
            literka = "P"
            assert literka not in alfabet, "W teście sprawdzającym poprawność znaków litera jest błędnie w alfabecie."

            with Generator(alfabet) as gen:
                wzorek = gen.Wzorzec(literka)

    def test_spelnialny(self):
        with self.assertRaises(UnsatisfiableError):
            alfabet = {"A": Fraction(1, 2), "B": Fraction(1, 2)}
            napis = "AAB"
            assert all(char in alfabet for char in napis), "W teście spełnialności napis niepoprawnie ma literki spoza alfabetu."

            n = Symbol("dlugosc")
            warunek = (n == len(napis)) & (n != len(napis))
            assert warunek == False, "W teście spełnialności warunek błędnie nie jest sprzeczny."

            with Generator(alfabet, warunek) as gen:
                wzorek = gen.Wzorzec(napis)



if __name__ == "__main__":
    unittest.main()
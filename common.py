# zewnetrzne
from fractions import Fraction
from typing import Callable, Protocol, TypeVar, Iterator, runtime_checkable, Literal
import re # regular expressions; wyrażenia regularne
import sympy

# nasze
from wyjatki import UnsatisfiableError

##############################################################################
T = TypeVar("T")
@runtime_checkable
class AppendableIterable(Protocol[T]):
    """
    Pomocnicza klasa do sprawdzania poprawności typów.
    Działa trochę jak concepts w C++
    """
    def append(self, item: T, /)  -> None: pass
    def __iter__(self) -> Iterator[T]: pass

def flatten(nestediterable: AppendableIterable[T]) -> AppendableIterable:
    """
    Funkcja spłaszczająca obiekty iterowalne z metodą append.
    :param nestediterable: Lista (lub inny obiekt iterowalny z metodą append), która może zawierać zagnieżdżone listy.
    :return: Płaska lista zawierająca wszystkie elementy zagnieżdżonych list.
    """
    def inner(flattenediterable: AppendableIterable[T], acc: AppendableIterable[T]):
        """
        Funkcja rekurencyjna w stylu Haskella, która w n-tym wywołaniu zwraca częściowo spłaszczoną listę.
        :param flattenediterable: Lista częściowo spłaszczona.
        :param acc: Akumulator (nowa lista produkowana z pierwszej).
        :return: Akumulator będący listą spłaszczoną bardziej niż przed wywołaniem.
        """
        for x in flattenediterable:
            if isinstance(x, AppendableIterable): # przechwytuje nawet te obiekty, które nie są list, ale z niej dziedziczą
                # zamiast list powinna być klasa, interfejs albo trait, który jednocześnie jest Iterable i "kontenerem" żeby odrzucić obiekty Iterable pokroju string etc.
                inner(x, acc)
            else:
                acc.append(x)
        return acc

    return inner(nestediterable, type(nestediterable)())
##############################################################################

class Symbol:
    """Klasa pomocnicza w celu budowy syntax sugar."""
    def __init__(self, name):
        self._sym = sympy.Symbol(name, real=True)

    def __eq__(self, other): return sympy.Eq(self._sym, other, evaluate=False)
    def __ne__(self, other): return sympy.Ne(self._sym, other, evaluate=False)
    def __lt__(self, other): return sympy.Lt(self._sym, other, evaluate=False)
    def __gt__(self, other): return sympy.Gt(self._sym, other, evaluate=False)
    def __ge__(self, other): return sympy.Ge(self._sym, other, evaluate=False)
    def __le__(self, other): return sympy.Le(self._sym, other, evaluate=False)

    __hash__ = object.__hash__

def ogranicz(alfabet: dict[Literal, Fraction], warunek: sympy.Expr | None = None, *args, **kwargs) -> Callable:
    """
    Funkcja ograniczająca dozwolone wartości i nakładająca konieczne warunki w stylu (x R n) gdzie x to długość napisu, R to relacja częściowego porządku, n to liczba naturalna.
    :param alfabet: Zbiór dozwolonych znaczków.
    :param warunek: Nałożony warunek na długość napisu.
    :param args: tak o żeby można było ewentualnie podawać do dalszych funkcji.
    :param kwargs: tak o żeby można było ewentualnie podawać do dalszych funkcji.
    :return: Dekorator klasy walidujący napisy przekazane do jej konstruktora.

    Inner jest wywoływany zgodnie z treścią https://docs.python.org/3/glossary.html#term-decorator
    """

    def inner(cls, *args, **kwargs) -> type:
        # sprawdzane jest tylko raz przy tworzeniu klasy
        if sum(alfabet.values()) != 1:
            raise ValueError(f"W klasie {cls.__name__} prawdopodobieństwa nie sumują się do 1.")

        if not sympy.satisfiable(warunek):
            raise UnsatisfiableError(f"W klasie {cls.__name__} warunki nie są spełnialne.")

        def waliduj(napis: str) -> str:
            # sprawdzane jest przy każdym wywołaniu konstruktora klasy
            if warunek is not None:
                length_sym = next(s for s in warunek.free_symbols if s.name == "dlugosc")
                if not warunek.subs(length_sym, len(napis)):
                    raise ValueError(f"Długość napisu {napis} nie spełnia warunków.")

            if re.fullmatch('(?:' + '|'.join(re.escape(litera) for litera in sorted(alfabet, key=len, reverse=True)) + ')+', napis) is None:
                raise ValueError(
                    f"Znaczki "
                    f"{", ".join(re.findall('[^' + "".join(re.escape(litera) for litera in sorted(alfabet, key=len, reverse=True)) + ']', napis))} "
                    f"są niedozwolone.")

            return napis

        original = cls.__new__
        cls.__new__ = \
            lambda self, napis, *initargs, **initkwargs: \
                (waliduj(napis), original(self, napis, *initargs, **initkwargs))[-1]

        return cls

    return inner









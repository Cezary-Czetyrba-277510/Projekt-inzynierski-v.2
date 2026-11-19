# zewnetrzne
import sys
from fractions import Fraction
from typing import Literal, Any

# nasze
from common import ogranicz
from ownstring import Wzorzec

from types import TracebackType

class Generator:
    @classmethod
    def zarejestruj(cls):
        return

    @classmethod
    def wstrzyknij(cls, klasa: type, args: dict[Literal, Any]):
        return type(
            f"fszczyknięty_{klasa.__name__}", (klasa,),
            args
        )

    def __init__(self, alfabet: dict[Literal, Fraction], warunek):
        self.alfabet = alfabet
        self.warunek = warunek

        self.Wzorzec = ogranicz(alfabet, warunek)(self.wstrzyknij(Wzorzec, {"alfabet": alfabet, "warunki": warunek}))

    def __enter__(self):
        return self

    def __getattr__(self, item):
        """Ta metoda specjalna wstrzykuje w sposób domyślny informacje o alfabecie do obiektów zależnych."""
        for module in sys.modules.values():
            if module is not None:
                namespace = vars(module)
                if item in namespace:
                    return namespace[item]
        return None


    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None):
        return False
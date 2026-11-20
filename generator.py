# zewnetrzne
from fractions import Fraction
from typing import Literal
from types import SimpleNamespace, TracebackType

# nasze
from common import ogranicz
from ownstring import Wzorzec
from markov import Markov
from traits import zalfabetyzuj

class Generator:
    def __init__(self, alfabet: dict[Literal, Fraction], warunek = None):
        self.alfabet = alfabet
        self.warunek = warunek
        self.namespace = SimpleNamespace()

    def __getattr__(self, name):
        try:
            return getattr(self.namespace, name)
        except AttributeError:
            try:
                return globals()[name]
            except KeyError:
                raise AttributeError(name) from None

    def __enter__(self):
        wzorzec = ogranicz(self.alfabet, self.warunek)(Wzorzec)
        setattr(self.namespace, wzorzec.__name__, wzorzec)

        markov = zalfabetyzuj(self.alfabet)(Markov)
        setattr(self.namespace, markov.__name__, markov)

        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None):
        return False
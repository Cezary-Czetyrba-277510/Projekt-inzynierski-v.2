from typing import Protocol, Any, ClassVar, TypeVar

class Drawable(Protocol):
    """
    Klasa interfejs w celu zabezpieczenia za pomocą typowania.
    https://en.wikipedia.org/wiki/Ad_hoc_polymorphism
    """
    def draw(self, *args, **kwargs) -> Any: pass

class Alphabetizable(Protocol):
    alfabet: ClassVar[dict[str, int] | set[str]]

T = TypeVar("T", bound=Alphabetizable)
def zalfabetyzuj(alfabet): # dekorator
    def decorate(cls: type[T]) -> type[T]:
        cls.alfabet = alfabet
        return cls
    return decorate
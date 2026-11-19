from typing import Protocol, Any

class Drawable(Protocol):
    """
    Klasa interfejs w celu zabezpieczenia za pomocą typowania.
    https://en.wikipedia.org/wiki/Ad_hoc_polymorphism
    """
    def draw(self, *args, **kwargs) -> Any: pass
from abc import abstractmethod
from collections import deque
from typing import Any, Protocol, runtime_checkable, Callable

from graphviz import Digraph
from traits import Drawable

# https://en.wikipedia.org/wiki/Breadth-first_search

class bfs:
    """
    Klasa reprezentująca algorytm breadth-first search.
    Właściwa funkcja implementująca bfs to funkcja search().
    Ta klasa implementuje domknięcie (leksykalne) za pomocą context-managementu (funkcje magiczne __enter__ i __exit__)
    Dobrzer wyglądająca składnia, nawet całkiem odpowiadająca semantyce przeszukiwania.
    """
    def __init__(self, root):
        self.root = root
        self.visited = set()
        self.current = None

        self.fifo = deque([self.root])
        self.visited = {self.root: 0}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def begin(self, lmbd: Callable, *args, **kwargs):
        """
        Algorytm przeszukiwania grafu wszerz.
        Dla grafów skierowanych bez cykli słownik visited nie jest potrzebny.
        Da się stwierdzić czy graf jest cykliczny za pomocą algorytmu Kahna (niżej).
        :param lmbd: Funkcja do wywołania na wierzchołku.
        :param args: Opcjonalne argumenty do lambdy.
        :param kwargs: Opcjonalne argumenty kluczowe do lambdy.
        :return: Nic. Wszelkie zmiany stanu są powodowane przez funkcję lmbd.

        Uwaga, aby nie zmieniać w danym wierzchołku wierzchołków sąsiadujących, ponieważ zmieni to zachowanie bfs.
        Dopuszczalne jest modyfikowanie zbioru wierzchołków odwiedzonych w callbacku definiowanym w kontekście ale trzeba być ostrożnym.
        """

        while self.fifo:
            self.current = self.fifo.popleft()

            for child in self.current.neighbors:
                if child not in self.visited:
                    self.visited[child] = len(self.visited)
                    self.fifo.append(child)

            lmbd(self.current, *args, **kwargs)

        return

# https://dl.acm.org/doi/10.1145/368996.369025
# https://en.wikipedia.org/wiki/Topological_sorting#Kahn's_algorithm
# to chyba nie jest potrzebne.
def kahn(root):
    return

@runtime_checkable
class NodeLike(Protocol):
    """
    Klasa interfejs w celu zabezpieczenia za pomocą typowania.
    https://en.wikipedia.org/wiki/Ad_hoc_polymorphism
    """
    wartosc: Any
    neighbors: list
    # end: bool

    @abstractmethod
    def __init__(self, wartosc: Any = None, *args: Any, **kwargs: Any) -> None: ...

    @property
    def terminal(self) -> bool:
        return False if self.neighbors is not None else True

class Node(NodeLike, Drawable):
    def __init__(self, wartosc: Any = None, neighbors: list | None = None, *args: Any, **kwargs: Any):
        self.wartosc = wartosc
        self.neighbors = [] if neighbors is None else neighbors # WAŻNE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # https://stackoverflow.com/questions/1132941/least-astonishment-and-the-mutable-default-argument

    def __getitem__(self, value):
        """
        Zwraca pierwszy napotkany wierzchołek o wartości równej value.
        :param value:
        :return:
        """
        for child in self.neighbors:
            if child.wartosc == value:
                return child
        return None

    def __repr__(self) -> str:
        return f"{self.wartosc}"

    def __str__(self) -> str:
        return repr(self)

    def draw(self, filename: str = "graph"):
        """
        Ta funkcja rysuje graf złożony z wierzchołków, do których można się dostać z tego wierzchołka.
        W szczególności dla korzenia rysuje cały spójny graf.
        Dla drzew skierowanych rysuje poddrzewo.
        :return:
        """
        dot = Digraph('G', filename=f"{filename}.gv", engine='sfdp')
        dot.node(str(id(self)), str(self.wartosc))

        with bfs(self) as search:
            def draw_edges(vertex):
                for this_node, other_node in vertex.edges:
                    dot.node(str(id(other_node)), str(other_node.wartosc))
                    dot.edge(str(id(this_node)), str(id(other_node)))

                return

            search.begin(draw_edges)

        return dot
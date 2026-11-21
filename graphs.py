# zewnętrzne
from functools import partial

from graphviz import Digraph

# nasze
from common import flatten
from nodes import Node, NodeLike, bfs
from traits import Drawable, Alphabetizable
from typecheck import implements
from ownstring import Wzorzec

class Graph(Drawable):
    pass

# Trie -> https://en.wikipedia.org/wiki/Trie
class Trie(Graph):
    """
    Klasa tworząca drzewo prefiksowe (trie).
    Ta klasa nie jest klasą, którą tworzy obiekty swojego typu (czyli nie powinno się używać jej konstruktora),
    ale jest klasą, którą buduje builder na podstawie dostarczonego typu (node_type)
    jusedż: x = Trie[Node](Wzorzec("ABC"), Wzorzec("BCA"))
    Trie[Node] wywołuje __class_getitem__ w definicji tej klasy i zwraca funkcję częściową z wypełnionym argumentem node_type
    Uwaga: node_type powinien implementować (niekoniecznie dziedziczyć po) klasie NodeLike (bo chcemy, żeby wierzchołkami były obiekty, które zachowują się jak wierzchołki)
    """
    def __class_getitem__[T: NodeLike](cls, node_type: type[T]) -> partial[T]:
        if not implements(node_type, NodeLike):
            raise TypeError(f"Typ powinien implementować atrybuty i metody jak z klasy {NodeLike.__name__}")
        return partial(cls.build, node_type=node_type)

    @staticmethod
    def build(wzorce: tuple[Wzorzec], *args, node_type: type[NodeLike], **kwargs):
        root = node_type()

        for wzorzec in wzorce:
            # Najpierw budujemy jedną odnogę grafu dla pierwszego wzorca, a później budujemy drugą odnogę, używając pierwszych N wierzchołków takich, że w N-tym wierzchołku skumulowany output
            # (sklejone literki z poprzednich wierzchołków) są maksymalnym wspólnym prefiksem pierwszego i drugiego wzorca.
            # w N+1 wierzchołku rozklejamy się na bok.

            node = root

            for char in wzorzec:
                child = next(
                    (child for child, label in node.neighbors if label == char),
                    None
                )

                if child is None:
                    child = node_type(wartosc=char, root=root, *args, **kwargs)
                    child.output = node.output + [char] # akumulacja literek występujących w poprzednich wierzchołkach
                    node.neighbors.append((child, char))

                node = child

            # Kiedy wyczerpiemy literki ze wzorca, możemy manualnie oznaczyć wierzchołek jako liść
            # albo możemy w definicji klasy wierzchołka napisać, że wierzchołek jest liściem, kiedy lista sąsiadów jest pusta.

            # node.end = True

        return root



class AhoCorasick(Alphabetizable, Graph):
    class AhoNode(Node):
        def __init__(self, root = None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.root = root if root is not None else self
            self.fail = None # po determinizacji fail również będzie None
            self.fail = None # Po determinizacji fail również będzie None,
            # ponieważ prekomputujemy przejścia tak, żeby każda kolejna literka dołączana do napisu
            # powodowała tylko jedno przejście pomiędzy wierzchołkami.

        @property
        def edges(self):
            edges = [(self, neighbor, {"label": f"{label}"}) for neighbor, label in self.neighbors]
            if self.fail:
                edges += [(self, self.fail, {"label": "fail", "color": "red", "style": "dotted"})]
            return edges

        @edges.setter
        def edges(self, new_edges):
            self.neighbors = new_edges
            return

        def next(self, char):
            return self[char] if self[char] is not None else self

        def fail_edge(self, root):
            """
            Funkcja budująca przejście "fail", czyli przejście, pod warunkiem że następna literka nie powoduje częściowego "przybliżenia się" do oczekiwanego napisu.
            :param root: Korzeń grafu.
            Niestety wierzchołek musi wiedzieć o tym, jaki jest korzeń,
            ponieważ w niektórych przypadkach bardzo głębokie wierzchołki mogą od razu przeskoczyć do pustego stanu.
            :return: Nic. Funkcja zmienia graf w miejscu.
            """
            # Ogólnie każdy wierzchołek W w takim grafie ma własność, że
            # wierzchołek "failowy" (połączony krawędzią fail z W) będzie płytszy niż ten W

            if self is root:
                # Na dzień dobry wszystkie wierzchołki bezpośrednio sąsiadujące z korzeniem mają fail-krawędzie do korzenia.
                # Konstrukcja drzewa prefiksowego gwarantuje nam, że nie ma dwóch wierzchołków, które odwołują się do siebie nawzajem na tej samej głębokości,
                # ponieważ drzewo prefiksowe scala te same prefiksy,
                # oraz że każdy wierzchołek-dziecko korzenia odwołuje się fail linkiem do korzenia (bo jedyny prefiks właściwy napisów jednoliterowych to pusty napis)

                for child, *_ in self.neighbors:
                    child.fail = root
                return

            for child, *_ in self.neighbors:
                # Czasami wierzchołek może być swoim własnym failem.
                # Przykład: alfabet {A, B}, wzorce ABB, ABA
                # wierzchołek reprezentujący stan A ma standardową krawędź tylko do AB, natomiast ma fail link do samego siebie.
                fail_node = self.fail

                # odpowiednikiem funkcji NEXT jest self.next()
                # node.next(char) zwraca obiekt, który jest następnikiem tego wierzchołka i ma wartość dokładnie (char)
                # lub siebie, jeżeli nie ma następnika z taką wartością
                # odpowiednikiem funkcji FAIL jest fail_edge
                # OUTPUT przy budowie jest raczej niepotrzebny
                while fail_node is not root and fail_node.next(child.wartosc) is fail_node:
                    fail_node = fail_node.fail

                child.fail = fail_node.next(child.wartosc) if fail_node.next(child.wartosc) is not fail_node else root

        def draw(self, filename: str = "graph"):

            dot = Digraph('G', filename=f"{filename}.gv", engine="sfdp")
            dot.attr(
                splines="true",
                overlap="false",
                sep="+20",
                esep="+10",
                concentrate="false"
            )

            dot.node(str(id(self)), str(self.wartosc))

            with bfs(self) as search:
                def draw_method(vertex):
                    for this_node, other_node, options in vertex.edges:
                        dot.node(str(id(other_node)), str("".join(other_node.output) if other_node.output else "root"))
                        dot.edge(str(id(this_node)), str(id(other_node)), **options)

                    return

                search.begin(draw_method)

            return dot
    # //AhoCorasickNode

    @classmethod
    def determinize(cls, root):
        """
        Determinizacja grafu, czyli (w skrócie) spowodowanie, że każda zmiana stanu powoduje wykonanie tylko jednego przejścia w grafie.
        :param root: Wierzchołek grafu. Niestety wierzchołek musi wiedzieć o tym, jaki jest korzeń,
        ponieważ w niektórych przypadkach bardzo głębokie wierzchołki mogą od razu przeskoczyć do pustego stanu.
        :return: Nic. Funkcja zmienia graf w miejscu.
        """
        # Słownik "memoizacyjny"
        new_edges = {}

        with bfs(root) as search:
            def inner(x):
                edges = []

                for char in cls.alfabet:
                    current_node = x
                    # Przeskakujemy z wierzchołka do momentu, aż znajdziemy wierzchołek z legalnym przejściem.
                    while current_node is not root and current_node.next(char) is current_node:
                        current_node = current_node.fail

                    # Kiedy znajdziemy wierzchołek z legalnym przejściem (last transition nie jest None), dołóżmy go do listy edges.
                    # Jeżeli takiego nie ma, dołóżmy przejście do stanu pustego (korzenia).
                    # Funkcja next przy braku znalezienia sąsiada o wartości char zwraca self.
                    last_transition = current_node.next(char)
                    edges.append((last_transition if last_transition is not current_node else root, char))

                new_edges[x] = edges

            search.begin(inner)

        # Krawędzie można legalnie zamienić dopiero po zastosowaniu algorytmu bfs.
        # W przeciwnym razie będziemy modyfikowali wierzchołki w trakcie iteracji po nich.
        # Być może jest to legalne w niektórych implementacjach, ale to jednak trochę trudne.

        for node, edges in new_edges.items():
            node.neighbors = edges
            node.fail = None

        return root

    def __new__(cls, *wzorce: Wzorzec, **kwargs):
        """
        Funkcja specjalna w celu zapobieżenia tworzeniu nowych obiektów klasy AhoCorasick (klasa powinna tworzyć graf i zwracać korzeń)
        :param wzorce: Wzorce.
        """
        builder = Trie[cls.AhoNode]
        root = builder(*wzorce)

        # zignorować błędy unexpected argument i błędy o typowaniu
        # chyba wbudowany type checker nie domaga i przy ewaluacji typu Trie[cls.AhoNode] od razu zakłada, że typ builder to klasa Trie, kiedy to nieprawda
        with bfs(root) as search:
            search.begin(lambda node: node.fail_edge(root))

        return root
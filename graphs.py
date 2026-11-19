# zewnetrzne
from functools import partial

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
    Ta klasa nie jest klasą która tworzy obiekty swojego typu (czyli nie powinno się używać jej konstruktowa)
    ale jest klasą która buduje builder na podstawie dostarczonego typu (node_type)
    jusedź: x = Trie[Node](Wzorzec("ABC"), Wzorzec("BCA"))
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
            # najpierw budujemy jedną odnogę grafu dla pierwszego wzorca, a później budujemy drugą odnogę używając pierwszych N wierzchołków takich, że w N-tym wierzchołku skumulowany output
            # (sklejone literki z poprzednich wierzchołków) są maksymalnym wspólnym prefiksem pierwszego i drugiego wzorca.
            # w N+1 wierzchołku rozklejamy się na bok.

            node = root

            for char in wzorzec:
                child = next(
                    (child for child in node.neighbors if child.wartosc == char),
                    None
                )

                if child is None:
                    child = node_type(wartosc=char, *args, **kwargs)
                    child.output = node.output + [char] # akumulacja literek występujących w poprzednich wierzchołkach
                    node.neighbors.append(child)

                node = child

            # kiedy wyczerpiemy literki ze wzorca możemy manualnie oznaczyć wierzchołek jako liść
            # albo możemy w definicji klasy wierzchołka napisać, że wierzchołek jest liściem kiedy lista sąsiadów jest pusta.
            # node.end = True

        return root

class AhoCorasick(Alphabetizable, Graph):
    class AhoNode(Node):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fail = None # po determinizacji fail również będzie None
            # ponieważ prekomputujemy przejścia tak, żeby każda kolejna literka dołączana do napisu
            # powodowała tylko jedno przejście pomiędzy wierzchołkami
            self.output = []

        @property
        def outgoing(self):
            a = []
            if self.fail is not None:
                a = [self.fail]

            return self.neighbors + a

        def get_subgraph_edges(self):
            return [(self, each) for each in self.neighbors] + flatten([each.get_subgraph_edges() for each in self.neighbors])

        @property
        def edges(self):
            a = []
            if self.fail is not None:
                a = [(self, self.fail)]

            return [(self, each) for each in self.neighbors] + a

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
                # na dzień dobry wszystkie wierzchołki bezpośrednio sąsiadujące z korzeniem mają fail-krawędzie do korzenia.
                # konstrukcja drzewa prefiksowego gwarantuje nam, że nie ma dwóch wierzchołków które odwołują się do siebie nawzajem na tej samej głębokości,
                # ponieważ drzewo prefiksowe scala te same prefiksy,
                # oraz że każdy wierzchołek-dziecko korzenia odwołuje się fail linkiem do korzenia (bo jedyny prefiks właściwy napisów jednoliterowych to pusty napis)

                for child in self.neighbors:
                    child.fail = root
                return

            for child in self.neighbors:
                # czasami wierzchołek może być swoim własnym failem.
                # przykład: alfabet {A, B}, wzorce ABB, ABA
                # wierzchołek reprezentujący stan A ma standardową krawędź tylko do AB, natomiast ma fail link do samego siebie.
                fail_node = self.fail

                # odpowiednikiem funkcji NEXT jest self.next()
                # node.next(char) zwraca obiekt, który jest następnikiem tego wierzchołka i ma wartość dokładnie (char)
                # lub siebie jeżeli nie ma następnika z taką wartością
                # odpowiednikiem funkcji FAIL jest fail_edge
                # OUTPUT przy budowie jest raczej niepotrzebny
                while fail_node is not root and fail_node.next(child.wartosc) is fail_node:
                    fail_node = fail_node.fail

                child.fail = fail_node.next(child.wartosc) if fail_node.next(child.wartosc) is not fail_node else root

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
                    # Przeskakujemy z wierzchołka do wierzchołka do momentu, aż znajdziemy wierzchołek z legalnym przejściem.
                    while current_node is not root and current_node.next(char) is current_node:
                        current_node = current_node.fail

                    # kiedy znajdziemy wierzchołek z legalnym przejściem (last transition nie jest None), dołóżmy go do listy edges.
                    # jeżeli takiego nie ma dołóżmy przejście do stanu pustego (korzenia).
                    # funkcja next przy braku znalezienia sąsiada o wartości char zwraca self.
                    last_transition = current_node.next(char)
                    edges.append(last_transition if last_transition is not current_node else root)

                new_edges[x] = edges

            search.begin(inner)

        # Krawędzie można legalnie zamienić dopiero po zastosowaniu algorytmu bfs.
        # W przeciwnym razie będziemy modyfikowali wierzchołki w trakcie iteracji po nich.
        # Być może jest to legalne w niektórych implementacjach ale to jednak trochę trudne.

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
        # chyba wbudowany type checker nie domaga i przy ewaluacji typu Trie[cls.AhoNode] od razu zakłada, że typ builder to klasa Trie kiedy to nieprawda
        with bfs(root) as search:
            search.begin(lambda node: node.fail_edge(root))

        return root
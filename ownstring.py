class StrHelper(str):
    @property
    def prefix(self) -> list[str]:
        return [self[:i] for i in range(1, len(self) + 1)]

    @property
    def suffix(self) -> list[str]:
        return [self[i:] for i in range(0, len(self))]

class Wzorzec(StrHelper):
    pass

def longest_prefix(napis: str, lista_prefixow: list[str]) -> str:
    longest_currently = ""
    for prefix in lista_prefixow:
        if napis.startswith(prefix) and len(longest_currently) < len(prefix) and napis != prefix:
            longest_currently = prefix

    return longest_currently  # pusty string ewaluuje się do False

def longest_suffix(napis: str, lista_suffixow: list[str]) -> str:
    longest_currently = ""
    for prefix in lista_suffixow:
        if napis.endswith(prefix) and len(longest_currently) < len(prefix) and napis != prefix:
            longest_currently = prefix

    return longest_currently  # pusty string ewaluuje się do False
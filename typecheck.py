def declared_members(cls: type) -> set[str]:
    members: set[str] = set()

    for base in cls.__mro__:
        members.update(base.__dict__.get("__annotations__", {}))
        members.update(
            name for name in base.__dict__
            if not name.startswith("_")
        )

    return members

def implements(cls: type, protocol: type) -> bool:
    """
    Funkcja sprawdzająca, czy klasa ma zaimplementowane atrybuty i metody z protocol.
    Konieczne z powodu ograniczenia na runtime check https://github.com/python/typing/pull/464
    """
    required: set[str] = set()

    for base in protocol.__mro__:
        required.update(base.__dict__.get("__annotations__", {}))
        required.update(
            name for name in base.__dict__
            if not name.startswith("_")
        )

    return required <= declared_members(cls)
class LFUNode[Key, Value](object):
    def __init__(
        self, key: Key | None, value: Value | None, freq_count: int = 1
    ) -> None:
        super().__init__()
        self._key = key
        self._value = value
        self._freq_count = freq_count
        self.prev: LFUNode[Key, Value] | None = None
        self.next: LFUNode[Key, Value] | None = None

    def get_key(self) -> Key | None:
        return self._key

    def get_value(self) -> Value | None:
        return self._value

    def get_freq_count(self) -> int:
        return self._freq_count


class FreqList[Key, Value](object):
    def __init__(self, freq_count: int) -> None:
        self._head = LFUNode[Key, Value](
            None, None, 0
        )  # Replace Key() and Value() with None
        self._tail = LFUNode[Key, Value](
            None, None, 0
        )  # Replace Key() and Value() with None
        self._freq_count = freq_count

    def insert_node(self, node: LFUNode[Key, Value]) -> None:
        assert self._head.next is not None, "[ERROR] self._head.next is None!"
        the_next: LFUNode[Key, Value] = self._head.next
        the_next.prev = node
        node.next = the_next
        self._head.next = node
        node.prev = self._head

    def remove_node(self, node: LFUNode[Key, Value]) -> None:
        assert node.prev is not None, "[ERROR] node.prev is None!"
        assert node.next is not None, "[ERROR] node.next is None!"
        the_prev = node.prev
        the_next = node.next
        the_prev.next = the_next
        the_next.prev = the_prev
        del node


class LFUCache[Key, Value](object):
    def __init__(self, capacity: int):
        _node_map: dict[Key, LFUNode[Key, Value]] = {}
        _freq_map: dict[int, FreqList[Key, Value]] = {}

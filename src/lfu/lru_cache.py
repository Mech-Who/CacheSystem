# standard
from typing import get_args

# third-party
from loguru import logger


class LFUNode[Key, Value]:
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

    def set_value(self, value: Value) -> None:
        self._value = value

    def get_freq_count(self) -> int:
        return self._freq_count

    def set_freq_count(self, freq_count) -> None:
        self._freq_count = freq_count


class IllegalOperationError(Exception): ...


class FreqList[Key, Value]:
    def __init__(self, freq_count: int) -> None:
        self._head = LFUNode[Key, Value](
            None, None, 0
        )  # Replace Key() and Value() with None
        self._tail = LFUNode[Key, Value](
            None, None, 0
        )  # Replace Key() and Value() with None
        self._head.next = self._tail
        self._tail.prev = self._head
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

    def is_empty(self) -> bool:
        if self._head.next == self._tail:
            return True
        return False

    def get_last_node(self) -> LFUNode[Key, Value]:
        if self.is_empty():
            raise IllegalOperationError("IllegalOperationError: Link list is empty!")
        return self._tail.prev


class LFUCache[Key, Value]:
    def __init__(self, capacity: int):
        self._capacity = capacity
        self._max_freq = 0
        self._node_map: dict[Key, LFUNode[Key, Value]] = {}
        self._freq_map: dict[int, FreqList[Key, Value]] = {}

    def get(self, key: Key) -> Value | None:
        # key不存在，返回默认值
        if key not in self._node_map.keys():
            return None
        # key存在，查值
        node = self._node_map[key]
        # 从原来频数链表中删除
        value = node.get_value()
        old_freq = node.get_freq_count()
        self.remove(node)
        # 更新频数并插入到新的频数链表
        self.insert(key, value, old_freq + 1)

    def put(self, key: Key, value: Value) -> None:
        if key in self._node_map.keys():
            # key存在，更新值与频数列表
            node = self._node_map[key]
            old_freq = node.get_freq_count()
            self.remove(node)
            self.insert(key, value, old_freq + 1)
        else:
            if len(self._node_map) >= self._capacity:
                # 缓存已满，换出频次最低的缓存
                for freq in range(1, self._max_freq + 1):
                    if not self._freq_map[freq].is_empty():
                        node = self._freq_map[freq].get_last_node()
                        self.remove(node)
                        break
            # 构造新节点并插入
            self.insert(key, value, 1)

    def insert(self, key: Key, value: Value, freq: int) -> None:
        node = LFUNode[Key, Value](key, value, freq)
        self._node_map[key] = node
        # 如果key中没有该频数，则创建新的频数链表
        if self._freq_map.get(freq) is None:
            self._freq_map[freq] = FreqList(freq)
        self._freq_map[freq].insert_node(node)
        if self._max_freq < freq:
            self._max_freq = freq

    def remove(self, node: LFUNode[Key, Value]) -> None:
        self._freq_map[node.get_freq_count()].remove_node(node)
        del self._node_map[node.get_key()]

    def create_default_value(self) -> Value:
        ValueType = get_args(self.__orig_class__)[1]  # 提取类型参数
        return ValueType()

    def create_default_key(self) -> Key:
        KeyType = get_args(self.__orig_class__)[0]  # 提取类型参数
        return KeyType()


if __name__ == "__main__":
    import random

    class DataNode(object):
        def __init__(self, data: int = -1) -> None:
            self._data = data

        def __str__(self):
            return f"{self._data}"

        def __repr__(self):
            return str(self)

    cache = LFUCache[int, DataNode](10)
    data_list = []
    for i in range(100):
        data_list.append(DataNode(random.randint(1, 10)))
    logger.debug(f"data_list: {data_list}")

    not_hit = 0
    for key, value in enumerate(data_list):
        v = cache.get(key)
        if v is None:
            # not hit
            cache.put(key, value)
            not_hit += 1
    total = len(data_list)
    logger.debug(
        f"total: {total}, hit: {total - not_hit}, hit rate: {(total - not_hit) / float(total):.2f}%"
    )

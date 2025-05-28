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

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"<{self._key}, {self._value} ({self._freq_count})>"


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

    def __repr__(self):
        return str(self)

    def __str__(self):
        data = "[ "
        node = self._head.next
        while node != self._tail:
            data += f"{node} "
            node = node.next
        data += "]"
        return data


class LFUCache[Key, Value]:
    def __init__(self, capacity: int):
        self._capacity = capacity
        self._max_freq = 0
        self._node_map: dict[Key, LFUNode[Key, Value]] = {}
        self._freq_map: dict[int, FreqList[Key, Value]] = {}

    def get(self, key: Key) -> Value | None:
        node = self._node_map.get(key)
        # key不存在，返回默认值
        if node is None:
            return None
        # key存在，查值
        # 从原来频数链表中删除
        value = node.get_value()
        old_freq = node.get_freq_count()
        self.remove(key)
        # 更新频数并插入到新的频数链表
        self.insert(key, value, old_freq + 1)
        return value

    def put(self, key: Key, value: Value) -> None:
        node = self._node_map.get(key)
        if node is not None:
            # key存在，更新值与频数列表
            logger.debug(f"[put] node is found: {self._node_map[key]}")
            old_freq = self._node_map[key].get_freq_count()
            self.remove(key)
            self.insert(key, value, old_freq + 1)
        else:
            logger.debug(
                f"[put] node not found - key({key}) not in _node_map({self._node_map.keys()})!"
            )
            if len(self._node_map) >= self._capacity:
                # 缓存已满，换出频次最低的缓存
                logger.debug("[put] cache is full!")
                for freq in range(1, self._max_freq + 1):
                    if not self._freq_map[freq].is_empty():
                        node = self._freq_map[freq].get_last_node()
                        self.remove(node.get_key())
                        break
            # 构造新节点并插入
            self.insert(key, value, 1)

    def insert(self, key: Key, value: Value, freq: int) -> None:
        # 创建新节点
        node = LFUNode[Key, Value](key, value, freq)
        # 如果key中没有该频数，则创建新的频数链表
        if self._freq_map.get(freq) is None:
            self._freq_map[freq] = FreqList(freq)
        # 插入节点到频数链表
        self._freq_map[freq].insert_node(
            node
        )  # 可能会导致插入链表的node和哈希表记录的node不是同一个node
        # self._freq_map[freq]._head.next.prev = node
        # node.next = self._freq_map[freq]._head.next
        # self._freq_map[freq]._head.next = node
        # node.prev = self._freq_map[freq]._head
        # 插入节点到hash表
        self._node_map[key] = node
        # 更新Cache中的最大频数
        if self._max_freq < freq:
            self._max_freq = freq

    def remove(self, key: Key) -> None:
        # 从链表中移除
        node = self._node_map[key]
        self._freq_map[node.get_freq_count()].remove_node(node)  # 可能有问题，但不确定
        # self._node_map[key].prev.next = self._node_map[key].next
        # self._node_map[key].next.prev = self._node_map[key].prev
        # 从哈希表中删除
        del self._node_map[key]

    def create_default_value(self) -> Value:
        ValueType = get_args(self.__orig_class__)[1]  # 提取类型参数
        return ValueType()

    def create_default_key(self) -> Key:
        KeyType = get_args(self.__orig_class__)[0]  # 提取类型参数
        return KeyType()

    def __repr__(self):
        return str(self)

    def __str__(self):
        data = f"all_nodes: {self._node_map}\n"
        data += "{\n"
        for key, value in self._freq_map.items():
            data += f"\t{key}: {value}\n"
        data += "}"
        return data


if __name__ == "__main__":
    import random
    import sys

    logger.remove()
    logger.add(sink=sys.stdout, level="DEBUG", colorize=True)

    class DataNode(object):
        def __init__(self, data: int = -1) -> None:
            self._data = data

        def __str__(self):
            return f"{self._data}"

        def __repr__(self):
            return str(self)

    cache_capacity = 10
    data_num = 100
    data_range = (1, cache_capacity * 2)
    Key = int
    Value = int

    cache = LFUCache[Key, Value](cache_capacity)
    data_list = []
    for i in range(data_num):
        data = random.randint(*data_range)
        data_list.append((data, Value(data)))
    logger.debug(f"data_list: {data_list}")

    not_hit = 0
    for key, value in data_list:
        logger.debug(f"{'=' * 50}")
        v = cache.get(key)
        if v is None:
            # not hit
            logger.debug("[cache.get] not found!")
            cache.put(key, value)
            not_hit += 1
            logger.debug(f"{not_hit=}")
        logger.debug(cache)
    total = len(data_list)
    logger.debug(
        f"total: {total}, hit: {total - not_hit}, hit rate: {(total - not_hit) / float(total) * 100:.2f}%"
    )

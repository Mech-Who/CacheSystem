import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.absolute()))

import random

import pytest
from loguru import logger

from src.lfu.lru_cache import LFUCache


class DataNode(object):
    def __init__(self, data: int = -1) -> None:
        self._data = data


@pytest.fixture
def cache() -> LFUCache[int, DataNode]:
    return LFUCache[int, DataNode](10)


@pytest.fixture
def data_list() -> list[DataNode]:
    dlist = []
    for i in range(100):
        dlist.append(DataNode(random.randint(1, 50)))
    return dlist


class TestLFUCache:
    def test_use_lfu_cache(
        self, cache: LFUCache[int, DataNode], data_list: list[DataNode]
    ) -> None:
        not_hit = 0
        for key, value in enumerate(data_list):
            v = cache.get(key)
            if v is None:
                # not hit
                cache.put(key, value)
                not_hit += 1
        total = len(data_list)
        logger.info(
            f"total: {total}, hit: {total - not_hit}, hit rate: {(total - not_hit) / float(total):.2f}%"
        )

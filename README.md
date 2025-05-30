# 缓存系统

## 一、项目介绍

## 二、缓存采用的算法

项目中所采用的缓存替换算法包含以下几个：

- LRU (Least Recently Used)
  - LRU-K
  - Hash LRU
- LFU (Least Frequently Used)
  - Align LFU
- ARC (...)

具体算法介绍如下

### 2.1 LRU 算法

> 参考：

算法思想：将最近最少被使用的缓存换出，换入新的缓存内容。

算法实现：通过 1 个双向链表和 1 个哈希表实现 $O(1)$ 的 `get` 和 `put` 操作 。其中双向链表用来记录缓存节点的时间维度信息（最近是否被使用），链表头部代表最近使用的节点。哈希表则用来通过 Key 直接查找到节点，无需在双向链表中进行查询即可获得节点，提高性能。

### 2.2 LFU 算法

> 参考：

算法思想：将缓存节点按照 访问频率 和 最近是否被访问 两个维度进行排序，优先换出访问频率低且最近未被访问的节点。

算法实现：通过 2 个哈希表和 N 个双向链表实现 $O(1)$ 的 `get` 和 `put` 操作。其中 1 个哈希表用来记录节点，提高查找性能。另一个哈希表用来记录每个频率次数和对应频率的节点的构成的双向链表。

### 2.3 ARC 算法

TBD...

## 三、项目环境

参见 `pyproject.toml` 文件的 `dependencies` 部分。

## 四、致谢

感谢卡哥提供的项目思路。

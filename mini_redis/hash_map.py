from __future__ import annotations

from typing import Generic, List, Optional, Tuple, TypeVar, Union, overload

from .linked_list import DoublyLinkedList, LinkedListNode


K = TypeVar("K")
V = TypeVar("V")
D = TypeVar("D")


class HashMapEntry(Generic[K, V]):
    """직접 구현한 해시 맵의 개별 체이닝 항목."""

    def __init__(self, key: K, value: V) -> None:
        self.key = key
        self.value = value


class HashMap(Generic[K, V]):
    """단순하고 결정적인 해시 함수를 사용하는 분리 체이닝 해시 맵."""

    def __init__(self, initial_capacity: int = 8) -> None:
        self._capacity = max(2, initial_capacity)
        self._buckets: List[Optional[DoublyLinkedList[HashMapEntry[K, V]]]] = [
            None
        ] * self._capacity
        self._size = 0

    def size(self) -> int:
        return self._size

    def put(self, key: K, value: V) -> Optional[V]:
        if (self._size + 1) / self._capacity > 0.75:
            self._resize(self._capacity * 2)
        return self._put_no_resize(key, value)

    @overload
    def get(self, key: K) -> Optional[V]:
        ...

    @overload
    def get(self, key: K, default: D) -> Union[V, D]:
        ...

    def get(self, key: K, default: object = None) -> object:
        node = self._find_node(key)
        if node is None:
            return default
        return node.data.value

    def remove(self, key: K) -> Optional[V]:
        bucket = self._bucket_for(key)
        if bucket is None:
            return None
        current = bucket.head
        while current is not None:
            if current.data.key == key:
                entry = bucket.remove_node(current)
                self._size -= 1
                return entry.value
            current = current.next
        return None

    def contains(self, key: K) -> bool:
        return self._find_node(key) is not None

    def keys(self) -> List[K]:
        result: List[K] = []
        for bucket in self._buckets:
            if bucket is not None:
                for entry in bucket.iter_values():
                    result.append(entry.key)
        return result

    def items(self) -> List[Tuple[K, V]]:
        result: List[Tuple[K, V]] = []
        for bucket in self._buckets:
            if bucket is not None:
                for entry in bucket.iter_values():
                    result.append((entry.key, entry.value))
        return result

    def _put_no_resize(self, key: K, value: V) -> Optional[V]:
        index = self._index_for(key)
        if self._buckets[index] is None:
            self._buckets[index] = DoublyLinkedList()
        bucket = self._buckets[index]
        if bucket is None:
            raise RuntimeError("hash map bucket was not initialized")
        current = bucket.head
        while current is not None:
            if current.data.key == key:
                old = current.data.value
                current.data.value = value
                return old
            current = current.next
        bucket.insert_back(HashMapEntry(key, value))
        self._size += 1
        return None

    def _resize(self, new_capacity: int) -> None:
        old_items = self.items()
        self._capacity = new_capacity
        self._buckets = [None] * self._capacity
        self._size = 0
        for key, value in old_items:
            self._put_no_resize(key, value)

    def _hash(self, key: K) -> int:
        text = str(key)
        value = 2166136261
        for char in text:
            value = value ^ ord(char)
            value = (value * 16777619) & 0xFFFFFFFF
        return value

    def _index_for(self, key: K) -> int:
        return self._hash(key) % self._capacity

    def _bucket_for(self, key: K) -> Optional[DoublyLinkedList[HashMapEntry[K, V]]]:
        return self._buckets[self._index_for(key)]

    def _find_node(self, key: K) -> Optional[LinkedListNode[HashMapEntry[K, V]]]:
        bucket = self._bucket_for(key)
        if bucket is None:
            return None
        current = bucket.head
        while current is not None:
            if current.data.key == key:
                return current
            current = current.next
        return None

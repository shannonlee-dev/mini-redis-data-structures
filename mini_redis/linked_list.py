from __future__ import annotations

from typing import Generic, Iterator, Optional, TypeVar


T = TypeVar("T")


class LinkedListNode(Generic[T]):
    """이중 연결 리스트의 노드."""

    def __init__(self, data: T) -> None:
        self.prev: Optional[LinkedListNode[T]] = None
        self.next: Optional[LinkedListNode[T]] = None
        self.data = data


class DoublyLinkedList(Generic[T]):
    """삽입, 제거, 이동을 O(1)에 수행하는 이중 연결 리스트."""

    def __init__(self) -> None:
        self.head: Optional[LinkedListNode[T]] = None
        self.tail: Optional[LinkedListNode[T]] = None
        self._size = 0

    def size(self) -> int:
        return self._size

    def insert_front(self, data: T) -> LinkedListNode[T]:
        node = LinkedListNode(data)
        node.next = self.head
        if self.head is not None:
            self.head.prev = node
        else:
            self.tail = node
        self.head = node
        self._size += 1
        return node

    def insert_back(self, data: T) -> LinkedListNode[T]:
        node = LinkedListNode(data)
        node.prev = self.tail
        if self.tail is not None:
            self.tail.next = node
        else:
            self.head = node
        self.tail = node
        self._size += 1
        return node

    def remove_front(self) -> Optional[T]:
        if self.head is None:
            return None
        return self.remove_node(self.head)

    def remove_back(self) -> Optional[T]:
        if self.tail is None:
            return None
        return self.remove_node(self.tail)

    def remove_node(self, node: LinkedListNode[T]) -> T:
        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = None
        node.next = None
        self._size -= 1
        return node.data

    def move_to_front(self, node: LinkedListNode[T]) -> LinkedListNode[T]:
        if node is self.head:
            return node
        if node.prev is not None:
            node.prev.next = node.next
        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = None
        node.next = self.head
        if self.head is not None:
            self.head.prev = node
        self.head = node
        if self.tail is None:
            self.tail = node
        return node

    def iter_values(self) -> Iterator[T]:
        current = self.head
        while current is not None:
            yield current.data
            current = current.next

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar, cast


T = TypeVar("T")


class DynamicArray(Generic[T]):
    """보너스 연습과 테스트에서 사용하는 작은 동적 배열."""

    def __init__(self, initial_capacity: int = 4) -> None:
        self._capacity = max(1, initial_capacity)
        self._size = 0
        self._items: List[Optional[T]] = [None] * self._capacity
        
    def __len__(self) -> int:
        return self._size

    def capacity(self) -> int:
        return self._capacity

    def append(self, value: T) -> None:
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._items[self._size] = value
        self._size += 1

    def get(self, index: int) -> T:
        self._check_index(index)
        return cast(T, self._items[index])

    def set(self, index: int, value: T) -> None:
        self._check_index(index)
        self._items[index] = value

    def remove(self, index: int) -> T:
        self._check_index(index)
        value = cast(T, self._items[index])
        for pos in range(index, self._size - 1):
            self._items[pos] = self._items[pos + 1]
        self._size -= 1
        self._items[self._size] = None
        return value

    def to_list(self) -> List[T]:
        result: List[T] = []
        for index in range(self._size):
            result.append(cast(T, self._items[index]))
        return result

    def _resize(self, new_capacity: int) -> None:
        new_items: List[Optional[T]] = [None] * new_capacity
        for index in range(self._size):
            new_items[index] = self._items[index]
        self._items = new_items
        self._capacity = new_capacity

    def _check_index(self, index: int) -> None:
        if index < 0 or index >= self._size:
            raise IndexError("index out of range")

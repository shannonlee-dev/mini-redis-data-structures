from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

from .linked_list import DoublyLinkedList


T = TypeVar("T")
OrderedT = TypeVar("OrderedT")


class BinaryTreeNode(Generic[T]):
    """이진 트리 순회 연습에 사용하는 노드."""

    def __init__(
        self,
        value: T,
        left: Optional[BinaryTreeNode[T]] = None,
        right: Optional[BinaryTreeNode[T]] = None,
    ) -> None:
        self.value = value
        self.left = left
        self.right = right


class BinaryTree(Generic[T]):
    """일반적인 순회 알고리즘을 제공하는 이진 트리."""

    def __init__(self, root: Optional[BinaryTreeNode[T]] = None) -> None:
        self.root = root

    def preorder(self) -> List[T]:
        result: List[T] = []
        self._preorder(self.root, result)
        return result

    def inorder(self) -> List[T]:
        result: List[T] = []
        self._inorder(self.root, result)
        return result

    def postorder(self) -> List[T]:
        result: List[T] = []
        self._postorder(self.root, result)
        return result

    def level_order(self) -> List[T]:
        result: List[T] = []
        if self.root is None:
            return result
        queue: DoublyLinkedList[BinaryTreeNode[T]] = DoublyLinkedList()
        queue.insert_back(self.root)
        while queue.size() > 0:
            node = queue.remove_front()
            if node is None:
                break
            result.append(node.value)
            if node.left is not None:
                queue.insert_back(node.left)
            if node.right is not None:
                queue.insert_back(node.right)
        return result

    def _preorder(self, node: Optional[BinaryTreeNode[T]], result: List[T]) -> None:
        if node is None:
            return
        result.append(node.value)
        self._preorder(node.left, result)
        self._preorder(node.right, result)

    def _inorder(self, node: Optional[BinaryTreeNode[T]], result: List[T]) -> None:
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.value)
        self._inorder(node.right, result)

    def _postorder(self, node: Optional[BinaryTreeNode[T]], result: List[T]) -> None:
        if node is None:
            return
        self._postorder(node.left, result)
        self._postorder(node.right, result)
        result.append(node.value)


class BinarySearchTree(Generic[OrderedT]):
    """삽입, 검색, 삭제, 정렬 순회를 지원하는 이진 검색 트리."""

    def __init__(self) -> None:
        self.root: Optional[BinaryTreeNode[OrderedT]] = None

    def insert(self, value: OrderedT) -> None:
        self.root = self._insert(self.root, value)

    def contains(self, value: OrderedT) -> bool:
        current = self.root
        while current is not None:
            if value == current.value:
                return True
            if value < current.value:
                current = current.left
            else:
                current = current.right
        return False

    def delete(self, value: OrderedT) -> None:
        self.root = self._delete(self.root, value)

    def inorder(self) -> List[OrderedT]:
        return BinaryTree(self.root).inorder()

    def _insert(
        self, node: Optional[BinaryTreeNode[OrderedT]], value: OrderedT
    ) -> BinaryTreeNode[OrderedT]:
        if node is None:
            return BinaryTreeNode(value)
        if value < node.value:
            node.left = self._insert(node.left, value)
        elif value > node.value:
            node.right = self._insert(node.right, value)
        return node

    def _delete(
        self, node: Optional[BinaryTreeNode[OrderedT]], value: OrderedT
    ) -> Optional[BinaryTreeNode[OrderedT]]:
        if node is None:
            return None
        if value < node.value:
            node.left = self._delete(node.left, value)
        elif value > node.value:
            node.right = self._delete(node.right, value)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            successor = self._minimum(node.right)
            node.value = successor.value
            node.right = self._delete(node.right, successor.value)
        return node

    def _minimum(self, node: BinaryTreeNode[OrderedT]) -> BinaryTreeNode[OrderedT]:
        current = node
        while current.left is not None:
            current = current.left
        return current

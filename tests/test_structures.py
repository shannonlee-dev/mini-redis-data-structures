"""자료구조의 충돌·확장·삭제·순서 경계를 공개 연산으로 검증한다."""

import pytest

from mini_redis.structures.dynamic_array import DynamicArray
from mini_redis.structures.hash_map import HashMap
from mini_redis.structures.linked_list import DoublyLinkedList
from mini_redis.structures.min_heap import HeapItem, MinHeap
from mini_redis.structures.tree import BinarySearchTree, BinaryTree, BinaryTreeNode


def test_hash_map_collision_chains_survive_resize_update_and_removal():
    class CollidingMap(HashMap):
        def _hash(self, key):
            return 0

    mapping = CollidingMap(initial_capacity=2)
    for index in range(30):
        mapping.put(f"key{index}", index)
    assert mapping.size() == 30
    for index in range(30):
        assert mapping.get(f"key{index}") == index
    assert mapping.put("key15", 100) == 15
    assert mapping.get("key15") == 100 and mapping.size() == 30
    for key in ["key0", "key15", "key29"]:
        assert mapping.remove(key) is not None
        assert not mapping.contains(key)
    assert mapping.size() == 27 and mapping.get("key1") == 1
    assert mapping.remove("missing") is None


def test_array_resize_and_middle_removal_preserve_order():
    array = DynamicArray(initial_capacity=1)
    for value in [1, 2, 3, 4, 5]:
        array.append(value)
    array.set(2, 30)
    assert array.remove(1) == 2
    assert array.to_list() == [1, 30, 4, 5]
    assert array.get(1) == 30 and len(array) == 4
    with pytest.raises(IndexError):
        array.get(-1)
    with pytest.raises(IndexError):
        array.remove(4)


def test_linked_list_moves_tail_and_removes_middle_without_losing_neighbors():
    linked = DoublyLinkedList()
    first = linked.insert_back("a")
    linked.insert_back("b")
    last = linked.insert_back("c")
    linked.move_to_front(last)
    assert list(linked.iter_values()) == ["c", "a", "b"]
    assert linked.remove_node(first) == "a"
    assert linked.remove_back() == "b"
    assert linked.remove_front() == "c"
    assert linked.size() == 0 and linked.head is None and linked.tail is None
    assert linked.remove_front() is None and linked.remove_back() is None


def test_heap_orders_expiry_then_key_and_handles_empty_pops():
    heap = MinHeap()
    for expiry, key in [(2, "a"), (1, "z"), (1, "b"), (3, "c")]:
        heap.push(HeapItem(expiry, key))
    results = []
    while heap.size():
        item = heap.pop()
        results.append((item.expire_at, item.key))
    assert results == [(1, "b"), (1, "z"), (2, "a"), (3, "c")]
    assert heap.peek() is None and heap.pop() is None


def test_binary_tree_traversal_orders():
    tree = BinaryTree(BinaryTreeNode(2, BinaryTreeNode(1), BinaryTreeNode(3)))
    assert tree.preorder() == [2, 1, 3]
    assert tree.inorder() == [1, 2, 3]
    assert tree.postorder() == [1, 3, 2]
    assert tree.level_order() == [2, 1, 3]
    assert BinaryTree().level_order() == []


def test_search_tree_deletes_two_child_root_without_losing_successor():
    tree = BinarySearchTree()
    for value in [4, 2, 6, 1, 3, 5, 7, 4]:
        tree.insert(value)
    assert tree.inorder() == [1, 2, 3, 4, 5, 6, 7]
    tree.delete(4)
    tree.delete(1)
    tree.delete(6)
    tree.delete(99)
    assert tree.inorder() == [2, 3, 5, 7]
    assert tree.contains(5) and not tree.contains(4)

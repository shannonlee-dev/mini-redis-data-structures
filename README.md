# Mini Redis Data Structures

A small Redis-style in-memory key-value store implemented in Python. The project focuses on the data structures behind fast lookup, key expiration, memory-bound eviction, and command dispatch.

It is not a full Redis clone. The goal is to make the tradeoffs visible: hash maps for lookup, a min heap for TTL cleanup, and a doubly linked list for LRU ordering.

## Features

- `SET`, `GET`, `DELETE`, `EXISTS`, `DBSIZE`, `KEYS`
- `EXPIRE` and `TTL`
- LRU eviction under a configurable memory limit
- Pub/Sub-style channel state
- Custom data structure implementations

## Run

```bash
python3 mini_redis.py
```

Example session:

```text
mini-redis> SET name redis
OK
mini-redis> GET name
"redis"
mini-redis> EXPIRE name 10
(integer) 1
mini-redis> TTL name
(integer) 10
mini-redis> QUIT
```

## Internal Model

```text
User input
  -> MiniRedisCLI
  -> MiniRedisStore
       -> HashMap for values
       -> HashMap for expiration timestamps
       -> MinHeap for nearest expiration
       -> DoublyLinkedList for LRU order
       -> HashMap for LRU node lookup
```

## Files

| File | Purpose |
| --- | --- |
| `mini_redis.py` | Entry point |
| `mini_redis/cli.py` | Command parsing and dispatch |
| `mini_redis/store.py` | Store, TTL, LRU, and memory-limit behavior |
| `mini_redis/hash_map.py` | Custom hash map |
| `mini_redis/linked_list.py` | Doubly linked list |
| `mini_redis/min_heap.py` | Expiration priority queue |
| `mini_redis/dynamic_array.py` | Supporting dynamic array |
| `mini_redis/tree.py` | Tree and BST practice implementation |
| `docs/EXPLANATION.md` | Longer Korean explanation |
| `STACK_QUEUE_DEQUE.md` | Stack, queue, and deque notes |

## Design Notes

- Lookup and metadata access are kept near O(1) with hash maps.
- Expiration cleanup is ordered by earliest deadline through a min heap.
- LRU eviction separates ordering from value storage.
- The implementation keeps the storage logic testable outside the CLI layer.

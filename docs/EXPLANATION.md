# Mini Redis 설명자료 V2

## 1. 프로젝트 한 문장 정의

> 이 프로젝트는 Python으로 만든 작은 Redis 스타일 인메모리 key-value 저장소입니다.
> 사용자는 `SET`, `GET`, `EXPIRE`, `TTL` 같은 명령을 입력하고, 프로그램은 값을 메모리에 저장하거나 조회하거나 만료시킵니다.

중요한 기준은 “Redis를 완전히 구현했다”가 아닙니다.
이 프로젝트는 실제 Redis의 모든 기능을 복제하는 것이 아니라, Redis의 핵심 아이디어를 자료구조 학습용으로 작게 구현한 프로젝트입니다.

중심 질문:

> 단순한 key-value 저장소를 만들 때, 어떤 자료구조를 조합하면 Redis와 비슷한 핵심 동작을 만들 수 있을까?

---

## 2. “이 프로그램이 무엇을 하는지”를 빠르게 고정시키기 위한 코드 설명 전 짧은 실행 예시

```bash
python3 mini_redis.py
```

예시 입력:

```text
SET name redis
GET name
EXISTS name
DBSIZE
KEYS
QUIT
```

예상 출력:

```text
mini-redis> OK
mini-redis> "redis"
mini-redis> (integer) 1
mini-redis> (integer) 1
mini-redis> 1. "name"
mini-redis>
```

예시 해석:

- `SET name redis`는 `name`이라는 key에 `redis`라는 value를 저장합니다.
- `GET name`은 저장된 값을 다시 꺼냅니다.
- `EXISTS name`은 key가 존재하는지 확인합니다.
- `DBSIZE`는 현재 저장된 key 개수를 보여줍니다.
- `KEYS`는 저장된 key 목록을 보여줍니다.

여기까지는 단순한 저장소처럼 보입니다.
하지만 이 프로젝트의 핵심은 여기서 끝나지 않습니다.

---

## 3. 단순 저장소에서 생기는 세 가지 문제

내부 구조로 넘어가는 출발 질문:

> 단순히 값을 저장하고 꺼내는 것만 하면 될까요?

이 프로젝트에서는 적어도 세 가지 문제가 생깁니다.

### 문제 1. key를 빠르게 찾아야 한다

`GET name`을 입력했을 때 전체 데이터를 처음부터 끝까지 찾으면 느립니다.
key로 value를 빠르게 찾아야 합니다.

필요한 자료구조: `HashMap`

```text
GET name
   |
   v
HashMap에서 name을 빠르게 찾음
   |
   v
"redis" 반환
```

### 문제 2. 일정 시간이 지나면 key가 사라져야 한다

Redis에는 `EXPIRE` 같은 기능이 있습니다.
이 프로젝트도 특정 key에 만료 시간을 줄 수 있습니다.

예를 들어:

```text
SET temp value
EXPIRE temp 10
TTL temp
```

이 경우 `temp`는 10초 뒤에 만료되어야 합니다.
그러려면 key별 만료 시간을 기억해야 하고, 어떤 key가 가장 먼저 만료되는지도 빠르게 알 수 있어야 합니다.

필요한 구조: `_expires`와 `MinHeap`

### 문제 3. 메모리 제한이 있으면 오래된 key를 제거해야 한다

메모리 제한을 걸면 모든 값을 무한히 저장할 수 없습니다.
제한을 넘으면 어떤 key를 버릴지 정해야 합니다.

이 프로젝트는 가장 오래 전에 사용된 key를 먼저 제거하는 LRU 방식을 사용합니다.

필요한 자료구조: `DoublyLinkedList`

```text
최근 사용됨                                      오래됨
head                                            tail
[user] <-> [session] <-> [temp] <-> [old-key]

메모리 초과 시 tail 쪽 old-key 제거
```

---

## 4. 전체 구조 지도

파일과 클래스의 위치를 잡는 전체 구조 지도입니다.

```text
사용자 입력
   |
   v
mini_redis.py
   |
   v
MiniRedisCLI
   |
   v
MiniRedisStore
   |
   +--> HashMap: 실제 key-value 저장
   |
   +--> HashMap: key별 만료 시간 저장
   |
   +--> MinHeap: 가장 빨리 만료될 key 관리
   |
   +--> DoublyLinkedList: LRU 순서 관리
   |
   +--> HashMap: key에서 LRU node로 바로 접근
   |
   +--> HashMap: Pub/Sub 채널 상태 관리
```

지도 해석:

> 사용자는 CLI에 명령을 입력합니다.
> CLI는 문자열을 해석해서 Store에 전달합니다.
> Store는 실제 데이터를 관리하는 중심 객체입니다.
> Store 내부에서는 HashMap, LinkedList, Heap 같은 자료구조가 역할을 나눠 동작합니다.

---

## 5. 파일별 역할 요약

프로젝트를 구성하는 파일과 각 파일의 책임입니다.

| 파일 | 역할 | 핵심 |
|---|---|---|
| `mini_redis.py` | 실행 진입점 | CLI를 실행하는 가장 바깥 파일 |
| `mini_redis/cli.py` | 명령어 해석 | 입력 문자열을 Store 메서드 호출로 바꿈 |
| `mini_redis/store.py` | 핵심 저장소 | 데이터, TTL, LRU, 메모리 제한을 관리 |
| `mini_redis/hash_map.py` | 해시맵 | key를 빠르게 찾기 위한 직접 구현 |
| `mini_redis/linked_list.py` | 이중 연결 리스트 | LRU 순서와 해시 충돌 체이닝에 사용 |
| `mini_redis/min_heap.py` | 최소 힙 | 가장 빨리 만료될 key를 관리 |
| `mini_redis/dynamic_array.py` | 동적 배열 | 자료구조 학습용 보조 구현 |
| `mini_redis/tree.py` | 트리와 BST | 트리 순회와 검색 트리 학습용 구현 |

핵심 흐름: `mini_redis.py -> cli.py -> store.py`

---

## 6. 첫 번째 축: 명령은 어떻게 흘러가는가

대표 명령 `SET name redis`가 프로그램 안에서 흘러가는 경로입니다.

```text
SET name redis
   |
   v
MiniRedisCLI.execute_line()
   |
   v
명령어가 SET인지 확인
   |
   v
인자 개수가 3개인지 확인
   |
   v
MiniRedisStore.set("name", "redis")
   |
   v
HashMap에 저장
   |
   v
LRU 순서 갱신
   |
   v
"OK" 반환
```

이 흐름의 핵심: CLI와 Store의 책임 분리.

CLI는 다음을 담당합니다.

- 입력 문자열 파싱
- 명령어 이름 확인
- 인자 개수 확인
- Store 메서드 호출
- 반환값을 사용자에게 출력

Store는 다음을 담당합니다.

- 실제 데이터 저장
- 만료 시간 확인
- 메모리 사용량 계산
- LRU 순서 관리
- eviction 처리

책임 분리의 효과: 입력 해석과 실제 저장소 로직을 따로 읽을 수 있습니다.

---

## 7. CLI: 입력 문자열을 Store 호출로 바꾸는 계층

`MiniRedisCLI`는 사용자가 입력한 문자열을 프로그램 내부 동작으로 바꾸는 계층입니다.

> CLI는 저장소 자체가 아니라, 저장소를 사용하는 인터페이스입니다.
> 사용자가 `SET name redis`라고 입력하면, CLI는 이 문자열을 나누고, 명령어가 `SET`인지 판단한 뒤, Store의 `set()` 메서드를 호출합니다.

핵심 흐름은 다음과 같습니다.

```text
입력: "SET name redis"
   |
   v
shlex.split()
   |
   v
["SET", "name", "redis"]
   |
   v
command = "SET"
   |
   v
self._set(parts)
   |
   v
self.store.set("name", "redis")
```

`shlex.split`의 역할: 단순 공백 분리보다 따옴표가 있는 입력을 더 자연스럽게 처리합니다.

예를 들어:

```text
SET message "hello redis"
```

따옴표 안의 `hello redis`를 하나의 value로 다루기 위한 처리입니다.

### CLI 관찰 포인트

- 명령어는 대문자로 바꿔 비교합니다.
- `EXIT` 또는 `QUIT`을 입력하면 종료합니다.
- `_require()`는 인자 개수를 검사하는 공통 함수입니다.
- `_write_result()`는 리스트 결과와 단일 문자열 결과를 다르게 출력합니다.

### 핵심 문장

> CLI는 명령어를 직접 처리하는 것이 아니라, 명령어를 해석해서 Store로 넘기는 역할을 합니다.

---

## 8. 두 번째 축: Store는 왜 중심인가

`MiniRedisStore`는 이 프로젝트의 핵심입니다.
실제 Redis 비슷한 동작은 대부분 Store에서 일어납니다.

Store 내부 상태:

```text
_data         : 실제 key-value 저장
_expires      : key별 만료 시간 저장
_expire_heap  : 만료 시간이 가까운 key부터 관리
_lru          : 최근 사용 순서 관리
_lru_nodes    : key로 LRU 노드를 바로 찾기
_channels     : Pub/Sub 채널 상태 저장
_maxmemory    : 메모리 제한
_used_memory  : 현재 사용 중인 메모리 추정치
_evicted_keys : LRU로 제거된 key 개수
```

세 묶음으로 보는 Store 상태:

### 묶음 1. 실제 데이터

```text
_data
```

여기에는 실제 key-value가 저장됩니다.
`HashMap`을 사용하기 때문에 평균적으로 빠르게 key를 찾을 수 있습니다.

### 묶음 2. 만료 관리

```text
_expires
_expire_heap
```

`_expires`는 특정 key의 만료 시각을 저장합니다.
`_expire_heap`은 가장 빨리 만료될 후보를 빠르게 찾기 위해 사용합니다.

### 묶음 3. 메모리와 LRU

```text
_lru
_lru_nodes
_maxmemory
_used_memory
_evicted_keys
```

메모리가 제한을 넘으면 오래 전에 사용된 key부터 제거해야 합니다.
그 순서를 관리하는 것이 `_lru`입니다.

---

## 9. `SET`: Store의 핵심 동작이 한 번에 드러나는 명령

`SET`은 저장, 메모리 계산, TTL 제거, LRU 갱신, eviction이 모두 연결되는 명령입니다.

`SET key value`의 내부 흐름:

```text
set(key, value)
   |
   v
만료된 key 먼저 정리
   |
   v
새 entry size 계산
   |
   v
기존 key인지 확인
   |
   +--> 새 key면 HashMap에 추가
   |
   +--> 기존 key면 value 갱신
   |
   v
used_memory 갱신
   |
   v
LRU 순서 갱신
   |
   v
기존 TTL 제거
   |
   v
maxmemory 초과 시 LRU eviction
   |
   v
"OK"
```

핵심 문장:

> `SET`은 단순히 값을 넣는 명령이 아니라, 저장소의 여러 보조 구조를 함께 일관성 있게 갱신하는 명령입니다.

핵심 변화 세 가지:

1. 값을 저장하면 LRU 순서도 바뀝니다.
2. 값을 새로 SET하면 기존 TTL은 제거됩니다.
3. 메모리 제한을 넘으면 오래된 key가 제거될 수 있습니다.

---

## 10. `GET`: 조회와 동시에 바뀌는 LRU 순서

`GET`은 값을 조회하는 명령입니다.
하지만 이 프로젝트에서는 조회만 하지 않습니다.

값을 성공적으로 조회하면 그 key는 “최근에 사용된 key”가 됩니다.
그래서 LRU 순서를 앞으로 이동시킵니다.

```text
초기 LRU 상태

head                         tail
[a] <-> [b] <-> [c]

GET c 실행

head                         tail
[c] <-> [a] <-> [b]
```

핵심 문장:

> LRU는 “최근에 사용된 데이터는 남기고, 오래 사용하지 않은 데이터는 먼저 버리자”는 정책입니다.

`GET`의 내부 흐름:

```text
get(key)
   |
   v
key가 만료되었는지 확인
   |
   +--> 만료됨: 삭제하고 None 반환
   |
   v
_data에서 key 조회
   |
   +--> 없음: None 반환
   |
   v
LRU에서 해당 key를 head로 이동
   |
   v
value 반환
```

`DoublyLinkedList`가 필요한 이유: 중간에 있는 노드를 제거해서 앞으로 옮기려면 이전 노드와 다음 노드를 모두 알아야 합니다.
단일 연결 리스트보다 이중 연결 리스트가 적합한 지점입니다.

---

## 11. HashMap: key를 빠르게 찾는 구조

HashMap은 이 프로젝트에서 가장 기본적인 자료구조입니다.
실제 데이터 저장뿐만 아니라 TTL 정보, LRU 노드 인덱스, 채널 상태에도 사용됩니다.

> HashMap은 key를 넣으면 그 key가 들어갈 배열 위치를 계산해서, 평균적으로 빠르게 값을 찾게 해주는 구조입니다.

구조:

```text
HashMap

buckets
  0: None
  1: [key="name", value="redis"]
  2: None
  3: [key="age", value="20"] <-> [key="city", value="seoul"]
  4: None
```

같은 버킷에 여러 key가 들어갈 수 있습니다.
이것을 충돌이라고 합니다.
이 프로젝트는 충돌을 `DoublyLinkedList`로 연결해서 해결합니다.

```text
bucket[3]

[age] <-> [city] <-> [score]
```

### HashMap 핵심 포인트

- key를 문자열로 바꿔 해시 값을 계산합니다.
- 해시 값에 capacity를 나눈 나머지로 버킷 인덱스를 정합니다.
- 충돌이 나면 같은 버킷의 연결 리스트에 저장합니다.
- 데이터가 많아져 load factor가 0.75를 넘으면 크기를 두 배로 늘립니다.

### HashMap과 Store의 연결

Store 안에서 HashMap은 여러 번 등장합니다.

```text
_data       : key -> StoreEntry(value)
_expires    : key -> expire_at
_lru_nodes  : key -> linked list node
_channels   : channel -> ChannelState
```

즉, HashMap은 “빠른 조회가 필요한 곳”에 반복해서 사용됩니다.

---

## 12. DoublyLinkedList: LRU 순서를 관리하는 구조

이중 연결 리스트는 각 노드가 앞 노드와 뒤 노드를 모두 알고 있는 구조입니다.

```text
None <- [A] <-> [B] <-> [C] -> None
        head              tail
```

각 노드는 다음 정보를 가집니다.

```text
prev
next
data
```

이 구조가 중요한 이유는 LRU 때문입니다.

LRU에서는 가장 최근에 사용한 key를 앞쪽에 두고, 가장 오래 전에 사용한 key를 뒤쪽에 둡니다.

```text
head                                      tail
[most recent] <-> [middle] <-> [least recent]
```

메모리 제한 초과 시 제거 대상: tail의 key.

```text
evict 대상 = tail
```

### 왜 이중 연결 리스트인가

중간 노드를 앞으로 옮길 때 다음 작업이 필요합니다.

1. 기존 위치에서 노드를 뗀다.
2. head 앞에 붙인다.
3. head와 tail 포인터를 갱신한다.

빠른 처리를 위해 필요한 정보: 이전 노드와 다음 노드.
따라서 `prev`, `next`를 모두 가진 이중 연결 리스트가 적합합니다.

### `_lru_nodes`가 같이 필요한 이유

연결 리스트만 사용할 때의 문제: 특정 key의 노드를 찾기 위해 처음부터 끝까지 탐색해야 합니다.

해결 구조: Store의 `_lru_nodes` HashMap.

```text
_lru_nodes

"name" -> name 노드의 주소
"age"  -> age 노드의 주소
```

효과: key로 노드를 바로 찾고, 그 노드를 O(1)에 앞으로 옮길 수 있습니다.

핵심 문장:

> LRU를 빠르게 구현하려면 “순서 관리용 연결 리스트”와 “key에서 노드로 가는 해시맵”이 함께 필요합니다.

---

## 13. TTL과 MinHeap: 만료 시간을 관리하는 두 구조

TTL은 Time To Live의 약자입니다.
특정 key가 얼마나 오래 살아 있을지를 의미합니다.

예시:

```text
SET temp value
EXPIRE temp 10
TTL temp
```

이 명령은 `temp` key가 10초 뒤에 만료되도록 설정합니다.

TTL 관리 구조:

```text
_expires
_expire_heap
```

### `_expires`

`_expires`는 key별 만료 시각을 저장합니다.

```text
_expires

"temp" -> 1710000010.5
"user" -> 1710000040.2
```

특정 key의 TTL 확인: `_expires`.

### `_expire_heap`

전체 만료 청소의 핵심: 가장 빨리 만료될 key를 빠르게 찾기.
해결 구조: 최소 힙.

```text
        temp@10s
       /        \
   user@40s    cache@70s
```

힙의 루트에는 가장 작은 expire_at이 옵니다.
즉, 가장 빨리 만료될 항목이 맨 위에 있습니다.

### 왜 `_expires`와 `_expire_heap`이 둘 다 필요한가

둘 중 하나만 있으면 부족합니다.

`_expires`만 있으면 특정 key의 만료 시간은 빠르게 찾을 수 있지만, 전체 key 중 가장 먼저 만료될 key를 찾으려면 모두 확인해야 합니다.

`_expire_heap`만 있으면 가장 빠른 만료 후보는 알 수 있지만, 특정 key의 현재 만료 시간이 무엇인지 확인하기 어렵습니다.

두 구조를 함께 쓰는 이유:

```text
특정 key TTL 확인       -> _expires
가장 빠른 만료 후보 확인 -> _expire_heap
```

---

## 14. lazy deletion: 명령 실행 시점에 정리되는 만료 key

이 프로젝트는 만료 시간이 되었다고 해서 백그라운드에서 자동으로 key를 지우는 구조가 아닙니다.
대신 명령이 실행될 때 만료된 key를 정리합니다.

lazy deletion 흐름:

```text
시간이 지남
   |
   v
key가 논리적으로 만료됨
   |
   v
다음 명령 실행
   |
   v
만료 여부 확인
   |
   v
실제 삭제
```

예를 들어 `GET temp`를 했는데 `temp`가 이미 만료되었다면, Store는 그 자리에서 `temp`를 삭제하고 `(nil)`을 반환합니다.

`_delete_expired()`는 힙을 보면서 만료된 항목을 정리합니다.

```text
while heap이 비어 있지 않다:
    가장 빠른 만료 항목을 본다
    아직 만료 전이면 멈춘다
    만료되었으면 heap에서 꺼낸다
    _expires의 현재 만료 시간과 일치하면 key를 삭제한다
```

중요 조건: “현재 만료 시간과 일치하면” 삭제.
이 조건이 필요한 이유: 같은 key에 `EXPIRE`를 여러 번 걸 수 있기 때문입니다.

예를 들어:

```text
EXPIRE temp 10
EXPIRE temp 100
```

heap에 남을 수 있는 예전 기록: `temp@10`.
하지만 `_expires`의 현재 값은 `temp@100`입니다.
따라서 heap에서 `temp@10`을 꺼냈을 때 바로 삭제하면 안 됩니다.
현재 `_expires` 값과 비교해 오래된 기록인지 확인해야 합니다.

핵심 문장:

> MinHeap은 만료 후보를 빠르게 찾는 구조이고, `_expires`는 그 후보가 아직 유효한 기록인지 검증하는 기준입니다.

---

## 15. 메모리 제한과 eviction

이 프로젝트는 `CONFIG SET maxmemory n` 명령으로 메모리 제한을 설정할 수 있습니다.

예시:

```text
CONFIG SET maxmemory 10
```

메모리 제한을 넘으면 Store는 LRU 기준으로 key를 제거합니다.

여기서 메모리 계산은 실제 Python 객체 크기를 정확히 재는 방식이 아닙니다.
단순화해서 key와 value의 UTF-8 바이트 길이를 합산합니다.

```text
entry_size = len(str(key).encode("utf-8")) + len(str(value).encode("utf-8"))
```

예를 들어:

```text
key   = "name"   -> 4 bytes
value = "redis"  -> 5 bytes
total = 9 bytes
```

> 실제 Redis나 Python 런타임의 정확한 메모리 모델은 훨씬 복잡합니다.
> 이 프로젝트에서는 자료구조와 eviction 정책을 이해하기 위해 단순한 바이트 길이 모델을 사용했습니다.

### eviction 흐름

```text
SET newkey newvalue
   |
   v
used_memory 증가
   |
   v
maxmemory 초과 여부 확인
   |
   +--> 초과하지 않음: 끝
   |
   +--> 초과함
          |
          v
       LRU tail key 삭제
          |
          v
       used_memory 감소
          |
          v
       아직 초과하면 반복
```

핵심 문장:

> maxmemory는 저장소에 제한을 만들고, LRU는 그 제한을 넘었을 때 어떤 key를 버릴지 결정하는 정책입니다.

---

## 16. Pub/Sub: 채널별 구독자 수와 메시지 목록

이 프로젝트에는 `PUBLISH`와 `SUBSCRIBE`도 있습니다.
하지만 실제 Redis의 네트워크 기반 Pub/Sub과 같은 수준은 아닙니다.

> 이 구현의 Pub/Sub은 실제 메시지 전달 시스템이라기보다, 채널별 구독자 수와 메시지 목록을 관리하는 간단한 상태 모델입니다.

내부 상태는 `ChannelState`가 가집니다.

```text
ChannelState

subscribers: 구독자 수
messages   : 발행된 메시지 목록
```

`SUBSCRIBE channel`을 하면:

```text
채널이 없으면 생성
subscribers += 1
```

`PUBLISH channel message`를 하면:

```text
채널이 없으면 0 반환
채널이 있으면 messages에 message 추가
현재 subscribers 수 반환
```

위치: 핵심 저장소보다 부가 기능에 가까운 단순 상태 모델.

---

## 17. DynamicArray와 Tree의 위치

`dynamic_array.py`와 `tree.py`는 Mini Redis 핵심 동작에 직접 연결되지는 않습니다.
하지만 자료구조 학습 프로젝트라는 맥락에서는 의미가 있습니다.

> Store의 핵심 기능은 HashMap, LinkedList, Heap을 중심으로 동작합니다.
> DynamicArray와 Tree는 별도의 자료구조 학습용 구현으로 포함되어 있습니다.

### DynamicArray

동적 배열은 capacity가 꽉 차면 더 큰 배열을 만들고 기존 값을 복사합니다.

```text
capacity 4
[A][B][C][D]

append E

capacity 8
[A][B][C][D][E][ ][ ][ ]
```

핵심 포인트:

- append는 보통 O(1)입니다.
- resize가 일어나면 O(n)입니다.
- 중간 remove는 뒤 원소들을 당겨야 하므로 O(n)입니다.

### BinaryTree와 BinarySearchTree

트리의 역할: 순회와 검색 트리 삭제 학습.

```text
        8
      /   \
     3     10
    / \      \
   1   6      14
```

순회:

- preorder: root -> left -> right
- inorder: left -> root -> right
- postorder: left -> right -> root
- level_order: 위에서 아래로, 왼쪽에서 오른쪽으로

BST에서는 inorder 결과가 정렬된 순서가 됩니다.

---

## 18. 핵심 명령별 설명 스크립트

실제로 말할 수 있는 문장형 요약입니다.

### SET

> `SET`은 key와 value를 저장하는 명령입니다.
> 하지만 내부적으로는 단순 저장보다 많은 일을 합니다.
> 먼저 만료된 key를 정리하고, 새 value의 메모리 크기를 계산합니다.
> 기존 key라면 값을 갱신하고, 새 key라면 HashMap에 추가합니다.
> 그리고 이 key가 최근에 사용되었으므로 LRU 순서를 갱신합니다.
> 마지막으로 메모리 제한을 넘으면 오래된 key부터 제거합니다.

### GET

> `GET`은 key로 value를 조회하는 명령입니다.
> 먼저 key가 만료되었는지 확인합니다.
> 만료되었다면 실제로 삭제하고 `(nil)`처럼 없는 값으로 처리합니다.
> key가 살아 있다면 HashMap에서 value를 가져오고, 최근에 사용된 key이므로 LRU에서 앞으로 이동시킵니다.

### EXPIRE

> `EXPIRE`는 key에 만료 시간을 설정하는 명령입니다.
> Store는 key별 만료 시간을 `_expires` HashMap에 저장하고, 동시에 `MinHeap`에도 만료 후보로 넣습니다.
> HashMap은 특정 key의 만료 시간을 확인하는 구조이고, MinHeap은 가장 빨리 만료될 key를 찾는 구조입니다.

### TTL

> `TTL`은 key가 얼마나 더 살아 있는지 확인하는 명령입니다.
> key가 없거나 이미 만료되었다면 -2를 반환합니다.
> key는 있지만 만료 시간이 없으면 -1을 반환합니다.
> 만료 시간이 있다면 현재 시간과 expire_at의 차이를 계산해 남은 초를 반환합니다.

### CONFIG SET maxmemory

> `CONFIG SET maxmemory`는 저장소가 사용할 수 있는 메모리 제한을 설정합니다.
> 이 프로젝트에서는 실제 객체 메모리가 아니라 key와 value의 UTF-8 바이트 길이를 기준으로 계산합니다.
> 제한을 넘으면 LRU tail에 있는 오래된 key부터 제거합니다.

### INFO memory

> `INFO memory`는 현재 메모리 상태를 보여줍니다.
> `used_memory`, `maxmemory`, `evicted_keys`를 출력해서 현재 저장소가 얼마나 사용 중이고, 몇 개의 key가 제거되었는지 확인할 수 있습니다.

---

## 19. 예상 질문과 답변

### 항목 1. 기본 명령과 기능 동작

#### Q. String 타입 기본 동작은 어떤 명령으로 확인할 수 있나요?

`SET`, `GET`, `DEL`, `EXISTS`, `DBSIZE`, `KEYS`로 확인할 수 있습니다.

- `SET key value`: key에 value를 저장합니다.
- `GET key`: key가 있으면 value를 반환하고, 없으면 `(nil)`을 반환합니다.
- `DEL key`: 삭제 성공 시 `(integer) 1`, 없으면 `(integer) 0`을 반환합니다.
- `EXISTS key`: 존재하면 `(integer) 1`, 없으면 `(integer) 0`을 반환합니다.
- `DBSIZE`: 현재 살아 있는 key 개수를 반환합니다.
- `KEYS`: 현재 저장된 key 목록을 출력합니다.

이 명령들은 모두 CLI에서 인자 개수를 확인한 뒤 `MiniRedisStore`의 메서드로 연결됩니다.
실제 key-value 저장은 `_data` HashMap이 담당합니다.

#### Q. maxmemory 설정 후 LRU 자동 제거는 어떻게 동작하나요?

`CONFIG SET maxmemory n`으로 메모리 제한을 설정합니다.
그 뒤 `SET`으로 새 key를 넣었을 때 `_used_memory`가 `_maxmemory`를 넘으면 `_evict_if_needed()`가 실행됩니다.

eviction 흐름:

1. `_used_memory > _maxmemory`인지 확인합니다.
2. `_lru.tail`에 있는 key를 고릅니다.
3. tail은 가장 오래 전에 사용된 key입니다.
4. `_delete_key(lru_key)`로 실제 데이터, TTL 정보, LRU 노드를 함께 삭제합니다.
5. 삭제가 성공하면 `_evicted_keys`를 1 증가시킵니다.
6. 아직 메모리 제한을 넘으면 같은 과정을 반복합니다.

즉, LRU 자동 제거는 “가장 오래 사용되지 않은 key부터 제거”하는 방식입니다.

#### Q. `INFO memory`는 어떤 형식으로 출력되나요?

`INFO memory`는 세 줄을 출력합니다.

```text
used_memory:<현재 사용량>
maxmemory:<설정된 제한>
evicted_keys:<LRU로 제거된 key 개수>
```

`used_memory`는 실제 Python 객체 크기가 아니라, key와 value를 문자열로 바꾼 뒤 UTF-8 바이트 길이를 합산한 값입니다.
`maxmemory`는 `CONFIG SET maxmemory`로 설정한 값입니다.
`evicted_keys`는 메모리 초과로 LRU 제거가 일어난 횟수입니다.

#### Q. TTL 관리는 어떻게 동작하나요?

TTL 관리는 `_expires` HashMap과 `_expire_heap` MinHeap이 함께 담당합니다.

- `_expires`: 특정 key의 현재 만료 시각을 저장합니다.
- `_expire_heap`: 가장 빨리 만료될 후보를 루트에 둡니다.

`EXPIRE key seconds`가 들어오면 현재 시간에 seconds를 더해 `expire_at`을 만들고, `_expires`와 `_expire_heap`에 모두 기록합니다.
`TTL key`는 key가 없으면 `-2`, key는 있지만 만료 시간이 없으면 `-1`, 만료 시간이 있으면 남은 초를 반환합니다.
만료된 key는 조회나 정리 과정에서 `_delete_key()`로 제거됩니다.

#### Q. 에러 처리는 어떤 방식으로 하나요?

CLI는 명령어와 인자 개수를 먼저 확인합니다.
잘못된 명령이면 다음과 같은 형식으로 반환합니다.

```text
(error) ERR unknown command '...'
```

인자 개수가 틀리면 다음 형식입니다.

```text
(error) ERR wrong number of arguments for '...' command
```

정수로 바꿀 수 없는 값이 들어오면 다음 형식입니다.

```text
(error) ERR value is not an integer or out of range
```

메모리 제한보다 큰 entry를 저장하려고 하면 OOM 에러를 반환합니다.

```text
(error) OOM command not allowed when used_memory > 'maxmemory'
```

### 항목 2. 직접 구현한 자료구조

#### Q. 이중 연결 리스트의 노드 구조는 어떻게 되어 있나요?

`LinkedListNode`는 세 값을 가집니다.

```text
prev
next
data
```

`prev`는 이전 노드, `next`는 다음 노드, `data`는 실제 저장 값을 의미합니다.
리스트 자체는 `head`, `tail`, `_size`를 가집니다.

이 구조 덕분에 다음 연산들이 O(1)에 처리됩니다.

- `insert_front`: head 앞에 새 노드 연결
- `insert_back`: tail 뒤에 새 노드 연결
- `remove_front`: head 노드 제거
- `remove_back`: tail 노드 제거
- `remove_node`: 이미 알고 있는 노드를 중간에서 제거
- `move_to_front`: 이미 알고 있는 노드를 앞으로 이동

단, `remove_node`와 `move_to_front`가 O(1)이려면 “노드 참조를 이미 알고 있다”는 조건이 필요합니다.
LRU에서는 `_lru_nodes` HashMap이 key에서 노드로 바로 가는 역할을 하므로 이 조건을 만족합니다.

#### Q. 직접 설계한 해시 함수는 어떤 과정을 거쳐 인덱스를 만드나요?

`HashMap._hash(key)`는 key를 문자열로 바꾼 뒤 문자 하나씩 처리합니다.
초기값은 `2166136261`이고, 각 문자에 대해 XOR와 곱셈을 수행합니다.
계산 결과는 `& 0xFFFFFFFF`로 32비트 범위에 맞춥니다.

흐름:

```text
key
 -> str(key)
 -> 문자별 XOR
 -> 16777619 곱셈
 -> 32비트 마스킹
 -> hash value
 -> hash % capacity
 -> bucket index
```

마지막에 `_index_for(key)`가 `hash % capacity`를 계산해서 버킷 인덱스를 만듭니다.

#### Q. 해시 충돌은 어떻게 해결하나요?

이 프로젝트는 separate chaining 방식을 사용합니다.
버킷 배열의 같은 인덱스에 여러 key가 들어오면, 그 버킷 안에 `DoublyLinkedList`를 만들고 `HashMapEntry`들을 연결합니다.

```text
bucket[3]
[key=age] <-> [key=city] <-> [key=score]
```

`put`은 해당 버킷의 리스트를 순회하면서 같은 key가 있으면 value를 갱신합니다.
같은 key가 없으면 리스트 뒤에 새 `HashMapEntry`를 추가합니다.
`get`과 `remove`도 같은 버킷의 체인을 순회해서 대상 key를 찾습니다.

#### Q. 로드 팩터 0.75 초과 시 버킷 2배 확장은 어떻게 하나요?

`put`을 하기 전에 `(size + 1) / capacity > 0.75`인지 확인합니다.
이 조건이 참이면 `_resize(capacity * 2)`를 호출합니다.

resize 절차:

1. 기존 모든 `(key, value)`를 `items()`로 모읍니다.
2. capacity를 2배로 바꿉니다.
3. 새 버킷 배열을 만듭니다.
4. size를 0으로 초기화합니다.
5. 기존 key-value를 새 capacity 기준으로 다시 해싱해서 넣습니다.

중요한 점은 capacity가 바뀌면 `hash % capacity` 결과가 달라질 수 있다는 것입니다.
그래서 기존 엔트리를 단순 복사하지 않고 반드시 다시 넣어야 합니다.

### 항목 3. LRU, TTL, eviction 흐름

#### Q. LRU에서 해시맵과 이중 연결 리스트는 각각 어떤 역할을 하나요?

LRU는 두 구조가 함께 있어야 빠르게 동작합니다.

- `DoublyLinkedList`: key들의 사용 순서를 저장합니다.
- `_lru_nodes` HashMap: key로 해당 리스트 노드를 바로 찾습니다.

리스트의 head는 가장 최근에 사용된 key이고, tail은 가장 오래 전에 사용된 key입니다.
메모리를 줄여야 할 때 tail을 제거하면 LRU 정책이 됩니다.

#### Q. 왜 LRU에 해시맵과 이중 연결 리스트가 둘 다 필요한가요?

연결 리스트만 있으면 특정 key의 노드를 찾기 위해 O(n) 탐색이 필요합니다.
해시맵만 있으면 “가장 오래된 key”라는 순서를 빠르게 알기 어렵습니다.

그래서 역할을 나눕니다.

```text
조회: key -> node    = HashMap
순서: head <-> tail  = DoublyLinkedList
```

이 조합 덕분에 조회된 key를 O(1)에 찾고, O(1)에 head로 이동할 수 있습니다.

#### Q. O(1) LRU 달성 원리는 무엇인가요?

O(1) LRU의 핵심은 “조회는 해시맵, 갱신은 리스트 이동”입니다.

1. key가 사용됩니다.
2. `_lru_nodes.get(key)`로 리스트 노드를 바로 찾습니다.
3. `move_to_front(node)`로 해당 노드를 head로 옮깁니다.
4. 메모리 초과 시 `_lru.tail`을 바로 찾습니다.
5. tail key를 삭제합니다.

노드를 이미 알고 있기 때문에 리스트 중간 삭제와 head 삽입이 O(1)에 끝납니다.

#### Q. TTL 관리에 왜 힙을 사용했나요?

TTL에서는 “가장 빨리 만료될 key”를 빠르게 찾는 것이 중요합니다.
MinHeap은 가장 작은 값을 루트에 두는 자료구조입니다.
여기서는 `expire_at`이 가장 작은 항목이 루트에 옵니다.

따라서 `_delete_expired()`는 heap의 루트만 보고 판단할 수 있습니다.

- 루트가 아직 만료 전이면 뒤의 항목들도 더 늦게 만료되므로 멈춥니다.
- 루트가 만료되었으면 pop하고 key를 삭제할지 확인합니다.

이 방식은 모든 key를 매번 순회하는 것보다 효율적입니다.

#### Q. 메모리 초과 시 eviction 흐름은 어떻게 되나요?

eviction은 `_evict_if_needed()`에서 처리됩니다.

단계:

1. `SET`에서 새 entry size를 계산합니다.
2. `_used_memory`를 갱신합니다.
3. `_maxmemory`가 0보다 크고 `_used_memory > _maxmemory`이면 eviction이 필요합니다.
4. `_lru.tail.data`에서 가장 오래된 key를 가져옵니다.
5. `_delete_key(lru_key)`를 호출합니다.
6. `_data`, `_expires`, `_lru_nodes`, `_lru`에서 관련 상태를 제거합니다.
7. 삭제된 key의 entry size만큼 `_used_memory`를 줄입니다.
8. 삭제가 성공하면 `_evicted_keys`를 1 증가시킵니다.
9. 아직 초과 상태면 반복합니다.

#### Q. `GET` 명령어 전체 흐름은 어떻게 되나요?

`GET key`의 흐름은 다음 순서입니다.

1. `_is_expired(key)`로 만료 여부를 확인합니다.
2. 만료되었다면 `_delete_key(key)`로 삭제하고 `None`을 반환합니다.
3. 만료되지 않았다면 `_data.get(key)`로 entry를 찾습니다.
4. entry가 없으면 `None`을 반환합니다.
5. entry가 있으면 `_touch_lru(key)`를 호출합니다.
6. `_touch_lru`는 해당 key의 LRU 노드를 head로 이동합니다.
7. value를 반환합니다.
8. CLI는 `None`이면 `(nil)`, 값이 있으면 `"value"` 형식으로 출력합니다.

즉, `GET`은 TTL 확인, 삭제 여부 판단, 값 조회, LRU 갱신이 순서대로 들어 있는 명령입니다.

### 항목 4. 확장 질문

#### Q. LRU 대신 LFU 정책을 구현한다면 자료구조를 어떻게 바꿔야 하나요?

LFU는 Least Frequently Used, 즉 가장 적게 사용된 key를 제거하는 정책입니다.
LRU가 “최근성”을 기준으로 한다면 LFU는 “사용 횟수”를 기준으로 합니다.

필요한 상태는 다음과 같습니다.

- key -> value 저장용 HashMap
- key -> frequency 저장용 HashMap
- frequency -> key 묶음 저장 구조
- 최소 frequency를 기억하는 값

자주 쓰는 방식은 `freq -> DoublyLinkedList` 구조입니다.
각 key는 현재 frequency에 해당하는 리스트에 들어갑니다.
`GET`이나 `SET`으로 key가 사용되면 frequency를 1 올리고, 기존 frequency 리스트에서 다음 frequency 리스트로 이동합니다.

```text
freq 1: [a] [b]
freq 2: [c]
freq 5: [d]
```

eviction 시에는 가장 낮은 frequency 리스트에서 key를 제거합니다.
동일 frequency 안에서는 LRU처럼 오래된 key를 제거하면 합리적입니다.

#### Q. 데이터가 10만 건으로 늘어나면 병목이 될 수 있는 부분은 어디인가요?

가능한 병목은 다음과 같습니다.

1. `KEYS`
   - 모든 버킷과 모든 key를 순회하므로 O(n)입니다.
   - 10만 건이면 한 번 호출이 꽤 무거워질 수 있습니다.

2. HashMap 충돌 체인
   - 해시 분포가 나쁘면 특정 버킷의 연결 리스트가 길어집니다.
   - 그러면 평균 O(1)에 가까운 조회가 최악 O(n)에 가까워질 수 있습니다.

3. resize
   - 로드 팩터 초과 시 전체 item을 다시 해싱합니다.
   - resize 순간에는 O(n) 비용이 발생합니다.

4. TTL heap의 오래된 기록
   - 같은 key에 `EXPIRE`를 여러 번 걸면 heap 안에 stale item이 남을 수 있습니다.
   - `_delete_expired()`에서 pop하면서 현재 `_expires`와 비교해야 합니다.

개선 방향:

- `KEYS` 대신 cursor 기반 `SCAN` 형태 도입
- 더 안정적인 해시 함수 또는 Python 내장 hash 활용 검토
- resize 비용을 분산하는 incremental rehashing
- TTL heap stale item 비율을 줄이는 보정 로직
- 테스트 규모가 커질 경우 성능 측정용 benchmark 추가

#### Q. `used_memory`에 자료구조 오버헤드까지 포함하면 무엇이 달라지나요?

현재 `used_memory`는 key와 value의 UTF-8 바이트 길이만 계산합니다.
자료구조 오버헤드는 포함하지 않습니다.

오버헤드를 포함하면 다음 요소들이 추가됩니다.

- `StoreEntry` 객체 비용
- `HashMapEntry` 객체 비용
- linked list node의 `prev`, `next`, `data` 참조 비용
- HashMap 버킷 배열 비용
- MinHeap 배열과 `HeapItem` 비용
- `_expires`, `_lru_nodes` 같은 보조 인덱스 비용

이렇게 바꾸면 같은 key-value라도 TTL이 있거나 LRU 노드가 있는 경우 더 많은 메모리를 사용한 것으로 계산됩니다.
즉, eviction 시점이 지금보다 더 빨라질 수 있습니다.

공정한 비교나 채점을 위해서는 메모리 모델을 명확히 고정해야 합니다.

예를 들어:

- key/value 바이트만 계산하는 단순 모델
- key/value + 고정 객체 비용을 더하는 모델
- Python의 `sys.getsizeof`를 사용하는 모델

채점에서는 어떤 모델을 쓰는지에 따라 `used_memory`와 eviction 결과가 달라질 수 있습니다.
따라서 기준 모델을 문서화하고, 테스트도 그 모델에 맞춰 작성해야 합니다.

---

## 20. 짧은 비유

구조를 빠르게 잡기 위한 짧은 비유입니다.

### CLI

CLI는 접수 창구입니다.
사용자가 말한 문장을 받아서 내부 담당자인 Store에게 넘깁니다.

### Store

Store는 운영 관리자입니다.
실제 데이터, 만료 시간, 사용 순서, 메모리 제한을 모두 조율합니다.

### HashMap

HashMap은 주소록입니다.
이름을 주면 어디에 값이 있는지 빠르게 찾습니다.

### DoublyLinkedList

DoublyLinkedList는 줄 세우기입니다.
최근 사용한 key를 앞으로 보내고, 오래된 key는 뒤에 남게 합니다.

### MinHeap

MinHeap은 가장 급한 일을 맨 위에 올려두는 우선순위 구조입니다.
가장 빨리 만료될 key를 먼저 보게 해줍니다.

---

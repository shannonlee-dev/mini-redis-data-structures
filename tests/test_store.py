"""자료구조 이동 후 TTL과 LRU의 경계 동작을 검증한다."""

from mini_redis.store import MiniRedisStore


def test_rescheduled_ttl_ignores_stale_heap_entry():
    now = [100.0]
    store = MiniRedisStore(clock=lambda: now[0])
    store.set("key", "value")
    store.expire("key", "5")
    store.expire("key", "10")
    now[0] = 106.0
    assert store.dbsize() == 1 and store.get("key") == "value"
    now[0] = 110.0
    assert store.get("key") is None and store.ttl("key") == -2
    assert store.used_memory() == 0


def test_set_clears_expiry_and_lru_uses_reads():
    now = [100.0]
    store = MiniRedisStore(clock=lambda: now[0])
    store.set("a", "1")
    store.expire("a", "1")
    store.set("a", "2")
    now[0] = 102.0
    assert store.ttl("a") == -1
    store.config_set_maxmemory("4")
    store.set("b", "3")
    assert store.get("a") == "2"
    store.set("c", "4")
    assert store.get("b") is None
    assert store.get("a") == "2" and store.get("c") == "4"
    assert store.evicted_keys() == 1


def test_utf8_memory_and_oversized_write_preserve_old_value():
    store = MiniRedisStore()
    store.config_set_maxmemory("6")
    assert store.set("가", "나") == "OK"
    assert store.used_memory() == 6
    assert store.set("가", "나다").startswith("(error) OOM")
    assert store.get("가") == "나" and store.used_memory() == 6


def test_lower_memory_limit_removes_expired_keys_before_live_lru():
    now = [100.0]
    store = MiniRedisStore(clock=lambda: now[0])
    store.config_set_maxmemory("4")
    store.set("a", "1")
    store.set("b", "2")
    store.expire("b", "1")
    now[0] = 102.0
    assert store.config_set_maxmemory("2") == "OK"
    assert store.get("a") == "1"
    assert store.get("b") is None
    assert store.used_memory() == 2 and store.evicted_keys() == 0

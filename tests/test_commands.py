"""명령 오류가 저장 상태를 바꾸지 않고 채널·메모리 기능이 연결되는지 확인한다."""

import pytest

from mini_redis.cli import MiniRedisCLI


@pytest.mark.parametrize(
    "command",
    [
        'SET "unterminated',
        "SET missing",
        "GET",
        "UNKNOWN",
        "CONFIG SET maxmemory -1",
        "CONFIG SET maxmemory bad",
        "INFO invalid",
        "EXPIRE a bad",
        "SUBSCRIBE",
        "PUBLISH a",
    ],
)
def test_invalid_command_preserves_stored_value(command):
    cli = MiniRedisCLI()
    cli.execute_line("SET a 1")
    assert cli.execute_line(command).startswith("(error)")
    assert cli.execute_line("GET a") == '"1"'
    assert cli.execute_line("DBSIZE") == "(integer) 1"


def test_memory_commands_expose_lru_eviction_and_keys():
    cli = MiniRedisCLI()
    assert cli.execute_line("CONFIG SET maxmemory 4") == "OK"
    for command in ["SET a 1", "SET b 2", "GET a", "SET c 3"]:
        cli.execute_line(command)
    assert cli.execute_line("EXISTS b") == "(integer) 0"
    assert cli.execute_line("DBSIZE") == "(integer) 2"
    assert cli.execute_line("INFO memory") == [
        "used_memory:4",
        "maxmemory:4",
        "evicted_keys:1",
    ]
    keys = cli.execute_line("KEYS")
    assert any('"a"' in row for row in keys) and any('"c"' in row for row in keys)
    assert cli.execute_line("DEL missing") == "(integer) 0"


def test_pubsub_counts_are_isolated_by_channel():
    cli = MiniRedisCLI()
    assert cli.execute_line("PUBLISH missing hello") == "(integer) 0"
    assert cli.execute_line("SUBSCRIBE news") == 'subscribed to "news" (1)'
    assert cli.execute_line("SUBSCRIBE news") == 'subscribed to "news" (2)'
    assert cli.execute_line("SUBSCRIBE other") == 'subscribed to "other" (1)'
    assert cli.execute_line('PUBLISH news "hello world"') == "(integer) 2"
    assert cli.execute_line("PUBLISH other hello") == "(integer) 1"

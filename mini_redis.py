#!/usr/bin/env python3
"""Mini Redis CLI 실행 진입점."""

from mini_redis.cli import MiniRedisCLI


def main() -> None:
    MiniRedisCLI().run()


if __name__ == "__main__":
    main()

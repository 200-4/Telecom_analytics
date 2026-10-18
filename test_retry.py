# test_retry.py
from src.retry import retry_with_backoff


# Fails twice, then succeeds on the third attempt
calls = {'count': 0}

@retry_with_backoff(max_attempts=3, base_delay=0.5)
def flaky_load():
    calls['count'] += 1
    if calls['count'] < 3:
        raise ConnectionError(f"timeout on attempt {calls['count']}")
    return f"loaded after {calls['count']} attempts"


# Always fails, so the decorator should give up
@retry_with_backoff(max_attempts=3, base_delay=0.5)
def always_fails():
    raise ConnectionError("database is unreachable")


def main():
    print("TEST 1: Transient failure that recovers")
    print("-" * 60)
    result = flaky_load()
    print(f"Result: {result}\n")
    assert calls['count'] == 3, "expected exactly 3 attempts"

    print("TEST 2: Permanent failure should give up and raise")
    print("-" * 60)
    try:
        always_fails()
        print("❌ FAIL: expected an exception")
    except ConnectionError as e:
        print(f"✅ PASS: raised after retries -> {e}")

    print("\n✅ Retry tests complete!")


if __name__ == "__main__":
    main()
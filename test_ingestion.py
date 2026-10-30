import sqlite3
from src.ingestion import run_ingestion
from src.dead_letter import DeadLetterQueue


def validate(record):
    if record.get('call_id') is None:
        return False, "missing call_id"
    if record.get('duration_seconds', 0) < 0:
        return False, "negative duration"
    return True, ""


def main():
    # ---- TEST 1: partial success + a batch that recovers on retry ----
    sample = [{'call_id': f'C{i}', 'duration_seconds': i * 10} for i in range(1, 9)]
    sample += [{'call_id': None, 'duration_seconds': 5},
               {'call_id': 'C99', 'duration_seconds': -3}]

    loaded_store = []
    attempts = {'n': 0}

    def fetch():
        return sample

    def load(batch):
        attempts['n'] += 1
        if attempts['n'] == 1:
            raise ConnectionError("temporary write lock")  # fails once
        loaded_store.extend(batch)

    print("TEST 1: partial success with a recovering load")
    print("-" * 60)
    summary = run_ingestion('test_ingest_cdr', 'cdr', 'call_record',
                            fetch, validate, load, base_delay=0.2)
    print(f"Summary: {summary}")

    assert summary['fetched'] == 10
    assert summary['loaded'] == 8, f"expected 8 loaded, got {summary['loaded']}"
    assert summary['failed'] == 2, f"expected 2 failed, got {summary['failed']}"
    assert len(loaded_store) == 8
    assert DeadLetterQueue('telecom.db').count(summary['run_id']) == 2
    print("✅ Test 1 passed\n")

    # ---- TEST 2: fetch that always fails should mark the run FAILED ----
    print("TEST 2: fetch that always fails")
    print("-" * 60)

    def bad_fetch():
        raise ConnectionError("source unreachable")

    try:
        run_ingestion('test_ingest_fail', 'cdr', 'call_record',
                      bad_fetch, validate, load, base_delay=0.2)
        print("❌ FAIL: expected an exception")
        return
    except ConnectionError:
        pass

    conn = sqlite3.connect('telecom.db')
    status = conn.execute(
        "SELECT status FROM pipeline_runs WHERE pipeline_name = 'test_ingest_fail' "
        "ORDER BY run_id DESC LIMIT 1"
    ).fetchone()[0]
    conn.close()
    assert status == 'FAILED', f"expected FAILED, got {status}"
    print("✅ Test 2 passed")

    print("\n✅ All ingestion tests passed!")


if __name__ == "__main__":
    main()
# test_cdr_loader.py
import sqlite3
from src.cdr_loader import CdrLoader


def make_batch():
    return [
        {
            'call_id': f'TEST_CDR_{i:03d}',
            'subscriber_id': 'TEST_SUB_001',
            'call_type': 'VOICE',
            'duration_seconds': 60 + i,
            'timestamp_start': '2026-10-01 10:00:00',
            'timestamp_end': '2026-10-01 10:01:00',
        }
        for i in range(1, 6)
    ]


def count_test_rows(db_path='telecom.db'):
    conn = sqlite3.connect(db_path)
    n = conn.execute(
        "SELECT COUNT(*) FROM staging_cdr WHERE call_id LIKE 'TEST_CDR_%'"
    ).fetchone()[0]
    conn.close()
    return n


def cleanup(db_path='telecom.db'):
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM staging_cdr WHERE call_id LIKE 'TEST_CDR_%'")
    conn.commit()
    conn.close()


def main():
    loader = CdrLoader('telecom.db', source_system='test')
    batch = make_batch()

    try:
        print("TEST 1: First load of 5 new records")
        print("-" * 60)
        inserted = loader.load(batch)
        print(f"Inserted: {inserted}")
        assert inserted == 5, f"expected 5, got {inserted}"
        assert count_test_rows() == 5
        print("✅ Test 1 passed\n")

        print("TEST 2: Reload the SAME batch (must insert nothing)")
        print("-" * 60)
        inserted = loader.load(batch)
        print(f"Inserted: {inserted}")
        assert inserted == 0, f"expected 0, got {inserted}"
        assert count_test_rows() == 5, "duplicates were created!"
        print("✅ Test 2 passed\n")

        print("TEST 3: Batch with 2 old + 2 new records (only new should insert)")
        print("-" * 60)
        mixed = batch[:2] + [
            {'call_id': 'TEST_CDR_006', 'subscriber_id': 'TEST_SUB_001',
             'call_type': 'SMS', 'timestamp_start': '2026-10-01 11:00:00',
             'timestamp_end': '2026-10-01 11:00:00'},
            {'call_id': 'TEST_CDR_007', 'subscriber_id': 'TEST_SUB_001',
             'call_type': 'DATA', 'timestamp_start': '2026-10-01 11:05:00',
             'timestamp_end': '2026-10-01 11:20:00'},
        ]
        inserted = loader.load(mixed)
        print(f"Inserted: {inserted}")
        assert inserted == 2, f"expected 2, got {inserted}"
        assert count_test_rows() == 7
        print("✅ Test 3 passed\n")

        print("✅ All CDR loader tests passed!")

    finally:
        cleanup()
        print(f"\nCleanup done. Test rows remaining: {count_test_rows()}")


if __name__ == "__main__":
    main()
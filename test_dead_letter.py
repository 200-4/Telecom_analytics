# test_dead_letter.py
from src.pipeline_runs import PipelineRunLogger
from src.dead_letter import DeadLetterQueue


def main():
    runs = PipelineRunLogger('telecom.db')
    dlq = DeadLetterQueue('telecom.db')

    # A run where some records are bad
    run_id = runs.start_run('test_dlq_load', rows_attempted=5)

    good = [{'call_id': 'C1', 'duration_seconds': 30},
            {'call_id': 'C2', 'duration_seconds': 45},
            {'call_id': 'C3', 'duration_seconds': 12}]
    bad = [{'call_id': 'C4', 'duration_seconds': -5},
           {'call_id': None, 'duration_seconds': 20}]

    loaded = 0
    for rec in good:
        loaded += 1  # pretend it was loaded

    for rec in bad:
        reason = ("negative duration" if rec['duration_seconds'] is not None
                  and rec['duration_seconds'] < 0 else "missing call_id")
        dlq.add(run_id, 'cdr', 'call_record', rec, reason)

    runs.finish_run(run_id, rows_loaded=loaded, rows_failed=len(bad))

    # Verify
    print(f"\nDead-letter rows for run {run_id}: {dlq.count(run_id)}")
    print("\nREJECTED RECORDS:")
    print("-" * 70)
    for fid, rtype, reason, record in dlq.fetch_for_run(run_id):
        print(f"#{fid}  {rtype:12s} {reason:20s} {record}")

    assert dlq.count(run_id) == 2, "expected 2 dead-letter rows"
    print("\n✅ Dead-letter test passed!")


if __name__ == "__main__":
    main()
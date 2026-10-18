# test_pipeline_runs.py
from src.pipeline_runs import PipelineRunLogger
import sqlite3


def main():
    logger = PipelineRunLogger('telecom.db')

    # Simulate a successful run
    run_ok = logger.start_run('test_successful_load', rows_attempted=100)
    logger.finish_run(run_ok, rows_loaded=100, rows_failed=0)

    # Simulate a run that fails
    run_bad = logger.start_run('test_failed_load', rows_attempted=100)
    logger.fail_run(run_bad, 'Simulated connection timeout', rows_loaded=40)

    # Show what was recorded
    conn = sqlite3.connect('telecom.db')
    rows = conn.execute(
        """SELECT run_id, pipeline_name, status, rows_attempted,
                  rows_loaded, rows_failed, error_summary
             FROM pipeline_runs
            ORDER BY run_id"""
    ).fetchall()
    conn.close()

    print("\nRUN HISTORY:")
    print("-" * 90)
    for r in rows:
        print(f"{r[0]:<4} {r[1]:<22} {r[2]:<9} attempted={r[3]:<5} "
              f"loaded={r[4]:<5} failed={r[5]:<5} error={r[6]}")


if __name__ == "__main__":
    main()
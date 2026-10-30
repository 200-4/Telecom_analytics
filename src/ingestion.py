from src.pipeline_runs import PipelineRunLogger
from src.dead_letter import DeadLetterQueue
from src.retry import retry_with_backoff

def run_ingestion(pipeline_name:str,
                  data_source: str,
                  record_type: str,
                  fetch_fn,
                  validate_fn,
                  load_fn,
                  db_path:str='telecom.db',
                  batch_size:int=1000,
                  base_delay:float=2.0) -> dict:
    """
    Run one ingestion.

    fetch_fn()            -> list of dict records
    validate_fn(record)   -> (is_valid: bool, reason: str)
    load_fn(batch)        -> None; MUST be idempotent (safe to re-run a batch)

    Returns a summary dict. Raises the original exception if the run fails.
    """
    runs = PipelineRunLogger(db_path)
    dlq = DeadLetterQueue(db_path)

    fetch = retry_with_backoff(max_attempts=3, base_delay=base_delay)(fetch_fn)
    load = retry_with_backoff(max_attempts=3, base_delay=base_delay)(load_fn)

    run_id = runs.start_run(pipeline_name)
    loaded = 0
    failed = 0
    records = []
    valid = []

    try:
        records = fetch()

        for record in records:
            is_valid, reason = validate_fn(record)
            if is_valid:
                valid.append(record)
            else:
                dlq.add(run_id, data_source, record_type, record, reason)
                failed += 1

        for start in range(0, len(valid), batch_size):
            batch = valid[start:start + batch_size]
            inserted = load(batch)
            # Loaders that return the number of new rows report that;
            # loaders that return None are assumed to have loaded the whole batch.
            loaded += inserted if inserted is not None else len(batch)

    except Exception as exc:
        runs.fail_run(run_id, str(exc), rows_loaded=loaded)
        raise

    skipped = len(valid) - loaded
    runs.finish_run(run_id, rows_loaded=loaded, rows_failed=failed)

    return {
        'run_id': run_id,
        'fetched': len(records),
        'loaded': loaded,
        'skipped_duplicates': skipped,
        'failed': failed,
    }
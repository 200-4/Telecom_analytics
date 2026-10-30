# run_cdr_ingestion.py
import sqlite3
from src.ingestion import run_ingestion
from src.cdr_loader import CdrLoader


def fetch_cdr(limit: int = 500) -> list:
    """Read a slice of staging_cdr as dicts, standing in for an upstream API."""
    conn = sqlite3.connect('telecom.db')
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT call_id, subscriber_id, peer_msisdn, call_type, duration_seconds, "
        "data_mb, timestamp_start, timestamp_end, cell_id, region, tariff_code, "
        "charge_amount, currency "
        "FROM staging_cdr ORDER BY call_id LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def validate_cdr(record: dict):
    """Reject records missing any NOT NULL field the loader requires."""
    required = ['call_id', 'subscriber_id', 'call_type',
                'timestamp_start', 'timestamp_end']
    for field in required:
        if record.get(field) in (None, ''):
            return False, f"missing {field}"
    return True, ""


def main():
    loader = CdrLoader('telecom.db', source_system='cdr_api')

    summary = run_ingestion(
        pipeline_name='cdr_daily_load',
        data_source='cdr',
        record_type='call_record',
        fetch_fn=fetch_cdr,
        validate_fn=validate_cdr,
        load_fn=loader.load,
        db_path='telecom.db',
        batch_size=200,
    )

    print("\nSUMMARY")
    print("-" * 40)
    for key, value in summary.items():
        print(f"{key:10s} {value}")


if __name__ == "__main__":
    main()
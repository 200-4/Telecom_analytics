-- Remove dead-letter rows from test runs first (must run before pipeline_runs)
DELETE FROM raw_failed_records
WHERE run_id IN (
    SELECT run_id FROM pipeline_runs WHERE pipeline_name LIKE 'test_%'
);

-- Then remove the test run records
DELETE FROM pipeline_runs WHERE pipeline_name LIKE 'test_%';
# Erasure requests

[Back to the README](../README.md)

> Use synthetic subjects in the demo. Review authorisation, target tables and
> scope before processing real requests. A dry run is not completed erasure,
> and lakehouse evidence does not establish deletion from sources or backups.

`pl_privacy_erasure` runs `nb_compliance_erasure.py` once per system. You pass
the subjects as job parameters. There is no request table.

| Parameter | Meaning |
| --- | --- |
| `subject_column` | The column that identifies a data subject, for example `rider_id` |
| `subject_ids` | Comma-separated IDs |
| `subject_ids_file` | Or an absolute Volume path to a file with one ID per line |
| `strategy` | `nullify` (default), `hash` or `redact`, used when a contract declares none |
| `hash_salt` | Salt for the `hash` strategy |
| `entity_filter` | Comma-separated entities. Blank means every contract |
| `dry_run` | `true` by default |
| `confirm` | Must be exactly `ERASE` to change data |
| `case_ref` | The request this answers, for example a ticket ID |

Only contracts that declare personal-data fields and contain `subject_column` are touched.

## Plan first

Run with the defaults to plan. A dry run counts matching rows in each table and
records the outcome `planned`. Nothing is changed.

```bash
databricks bundle run erasure -t dev -p rideflow_dev \
  --params subject_column=rider_id,subject_ids=rid_123
```

## Apply

Data changes only when all three are set: `dry_run=false`, `confirm=ERASE` and a
non-empty `case_ref`.

- `dry_run=false` without `confirm=ERASE` records `not_run` and fails the task.
- `dry_run=false` and `confirm=ERASE` without `case_ref` fails before any change.

After applying `nullify` or `redact`, the notebook checks whether matching rows
still hold personal data. If any do, it records `incomplete` and fails the task.

## Evidence

Each run writes rows to `lakelogic_erasure_evidence`, beside the domain's
`lakelogic_run_log`. A row records the table, outcome, matched rows, strategy,
mode and `case_ref`. Subject IDs are never stored. The run records their count
and a SHA-256 digest instead, so you can match it to the request's own ID list.

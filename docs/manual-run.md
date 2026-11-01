# Run the RideFlow demo step by step

The `pl_data_00_mesh_orchestrator` job runs setup, seeds synthetic data, then runs every system in dependency order. This guide runs the same notebooks one at a time so you can inspect each stage.

The examples use the `marketplace / rideflow` system. Its tables are built in the `rideflow_dev_marketplace` catalog. There is no separate platform catalog: each domain catalog holds its own landing files, run logs and tables.

## Before you start

The notebooks read contracts from the workspace, not from a Volume. Set `contracts_root` to the workspace folder that holds the `contracts/` tree:

- After `databricks bundle deploy`, the bundle syncs `contracts/` under its root, `/Workspace/Shared/lakelogic-rideflow-databricks-governed-lakehouse/dev`. The jobs pass `contracts_root` as `${workspace.file_path}/contracts`.
- In a Git folder, use the path of its `contracts` folder, for example `/Workspace/Users/<you>/<repo>/contracts`.

Each notebook loads `<contracts_root>/<domain>/<system>/_system.yaml`.

## 1. Provision the structures

Open `platform/databricks/notebooks/nb_00_setup.py` and set:

```text
catalog = rideflow_dev
contracts_root = <your contracts folder>
environment = dev
```

Select **Run All**. The notebook reads every `_system.yaml` under `contracts_root` and creates:

- One catalog per domain (`rideflow_dev_<domain>`), with the `bronze`, `silver`, `gold`, `quarantine` and `lakelogic` schemas the registries declare
- A `files` schema in each domain catalog, with the `landing` and `lakelogic_logs` Volumes

It does not create the tables. In the `pl_admin_setup` job, a `ddl_<domain>_<system>` task runs `nb_pipeline_driver.py` with `ddl_only = true` for each system after setup. Running the notebook by hand, the pipeline driver creates the tables on its first run.

If your metastore has no default storage, set `catalog_storage_root` so new catalogs get a managed location. Setup is safe to run again.

## 2. Generate landing data

Seed before the first pipeline run. The landing Volumes are empty after setup, so Bronze has nothing to read until synthetic files exist. Seed again whenever you want new windows of data.

Open `platform/databricks/notebooks/nb_test_data_driver.py` and set:

```text
catalog = rideflow_dev
contracts_root = <your contracts folder>
domain = marketplace
system = rideflow
environment = dev
```

Select **Run All**. The notebook writes synthetic Bronze files into the system's landing Volume, `/Volumes/rideflow_dev_marketplace/files/landing/rideflow`. `invalid_ratio` (default `0.1`) and `duplicate_ratio` (default `0.05`) add bad and duplicate rows so contract failures can be inspected later.

The bundle job for this step is `pl_test_synthetic_seed`. It seeds every system that ingests files.

## 3. Process the medallion

Open `platform/databricks/notebooks/nb_pipeline_driver.py` and set:

```text
catalog = rideflow_dev
contracts_root = <your contracts folder>
domain = marketplace
system = rideflow
environment = dev
engine = spark
storage_mode = catalog
target_layers = bronze, silver, gold
```

Select **Run All**. LakeLogic resolves the declared dependencies and processes Bronze, Silver, and Gold in order. Rows that fail configured contract rules are routed to quarantine when policy allows the valid rows to continue.

![Databricks pipeline run summary](images/data_mesh_pipeline_log.png)

The structured run log records contract status, row counts, engine, and duration for each stage.

> `reset_layers` and `reload_layers` are empty by default, so nothing is dropped or truncated. Set `reset_layers` (DROP) or `reload_layers` (TRUNCATE) to a list of layers when you want a clean run. Leaving them empty does not mean append: each contract's materialization decides how it writes. In the RideFlow registries Bronze appends and Silver and Gold merge, and individual contracts can override that.

## 4. Inspect the outputs

Run the following in a Databricks SQL editor:

```sql
USE CATALOG rideflow_dev_marketplace;
SHOW SCHEMAS;
SHOW TABLES IN gold;
SHOW TABLES IN quarantine;

SELECT *
FROM gold.gold_fact_trip_completed
LIMIT 20;
```

Then select one of the tables returned by `SHOW TABLES IN quarantine` and inspect its failed rows and error context.

## Run another domain

Change `domain` and `system` in both drivers, for example `domain = payments` and `system = stripe`. Run the test-data driver, then the pipeline driver. Table names and dependencies are resolved from the contracts under `contracts/`.

If you deployed the Asset Bundle, you can run a system job instead. A system job runs Bronze, Silver and Gold only. It does not generate data, so run `synthetic_seed` first if the landing Volume is empty:

```bash
databricks bundle run synthetic_seed -t dev -p rideflow_dev
databricks bundle run payments_stripe -t dev -p rideflow_dev
databricks bundle run marketing_google_ads -t dev -p rideflow_dev
```

## Clean up

If you deployed the bundle, run these commands from `platform/databricks/`:

```bash
databricks bundle destroy -t dev -p rideflow_dev
for domain in business marketing marketplace operations payments reference shared; do
  databricks catalogs delete "rideflow_dev_${domain}" --force -p rideflow_dev
done
```

If you used only the notebooks, the catalog deletions are enough because no bundle-managed jobs or workspace files were deployed.

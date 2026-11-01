# Provision RideFlow directly in Databricks

Use this path when you want to inspect the catalogs and tables without installing the Databricks CLI or deploying an Asset Bundle.

## What this path does

The `nb_00_setup.py` notebook reads every `_system.yaml` under `contracts/` and creates one catalog per domain, the layer schemas, and the landing and log Volumes. The pipeline driver creates the tables.

It does **not** deploy the schedulable jobs that come with the Databricks Asset Bundle. Use the main README Quickstart when you want the complete job-based demo.

## Provision the structures

1. In Databricks, open **Workspace > Create > Git folder**.
2. Clone this GitHub repository.
3. Open `platform/databricks/notebooks/nb_00_setup.py`.
4. Attach the notebook to serverless compute or another Unity Catalog-enabled cluster.
5. Set the widgets:
   - `catalog`: `rideflow_dev`.
   - `contracts_root`: the workspace path of the Git folder's `contracts` folder, for example `/Workspace/Users/<you>/<repo>/contracts`.
   - `environment`: `dev`, the only environment the registries define.
   - `catalog_storage_root`: blank, unless your metastore has no default storage.
6. Select **Run All**.

The domain catalogs are named `rideflow_dev_<domain>` by `domain_catalog_prefix` in each `_system.yaml`. The notebook is idempotent, so it is safe to run again.

## Generate and process data

After provisioning, use the notebooks described in [Run the demo step by step](manual-run.md):

1. Run `nb_test_data_driver.py` to generate synthetic landing data.
2. Run `nb_pipeline_driver.py` to create the tables and process Bronze, Silver, and Gold.

Alternatively, deploy the Asset Bundle later. Run `pl_test_synthetic_seed`, then one of the per-system jobs (`pl_data_<domain>_<system>`).

## Which setup path should you choose?

| Goal | Recommended path |
| --- | --- |
| See the catalogs, schemas and Volumes quickly | `nb_00_setup.py` notebook |
| Run the complete scheduled workflow | Asset Bundle Quickstart in the README |
| Inspect every stage manually | [Manual run guide](manual-run.md) |

## Clean up

The notebook creates Unity Catalog objects at runtime. Remove them when finished:

```bash
for domain in business marketing marketplace operations payments reference shared; do
  databricks catalogs delete "rideflow_dev_${domain}" --force -p rideflow_dev
done
```

If you later deployed the Asset Bundle, also run `databricks bundle destroy` from the `platform/databricks/` directory to remove its jobs and synced workspace files.

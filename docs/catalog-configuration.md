# Use different Unity Catalog catalogs

The demo uses one catalog per domain: `rideflow_dev_<domain>`. Each holds that domain's layer schemas, quarantine, run logs, and a `files` schema with the `landing` and `lakelogic_logs` Volumes. There is no separate platform catalog.

## Where the names come from

Each system's `_system.yaml` sets its own locations under `environments: dev:`:

```yaml
environments:
  dev:
    project_root: /Workspace/Shared/lakelogic-rideflow-databricks-governed-lakehouse/dev
    domain_catalog_prefix: rideflow_dev
    log_path: /Volumes/rideflow_dev_{domain}/files/lakelogic_logs
    catalog: ${DATABRICKS_DEV_CATALOG}
    ls_catalog: rideflow_dev
    ls_schema: files
    ls_volume: landing
```

- Tables go to `<domain_catalog_prefix>_<domain>.<layer>`.
- Landing files go to `/Volumes/<ls_catalog>_<domain>/files/landing/<system>`.
- Run logs go to `log_path`.

To use other catalog names, change `domain_catalog_prefix`, `ls_catalog` and `log_path` in every `contracts/*/*/_system.yaml`. Keep them consistent across systems, because Shared products read other domains' catalogs.

## Notebook parameters

Every notebook takes the same core parameters:

| Parameter | Meaning |
| --- | --- |
| `catalog` | Passed to the registry as `DATABRICKS_<ENV>_CATALOG` |
| `contracts_root` | Workspace folder holding the `contracts/` tree |
| `domain` / `system` | Which `<contracts_root>/<domain>/<system>/_system.yaml` to load |
| `environment` | A key under `environments:` in `_system.yaml`; only `dev` exists |

`nb_00_setup.py` takes `catalog`, `contracts_root` and `environment` only. It reads every registry under `contracts_root`.

## Asset Bundle variables

`platform/databricks/databricks.yml` defines the variables the jobs pass to the notebooks. Override them under `targets: dev: variables:`, or with `--var` on the command line.

| Variable | Use |
| --- | --- |
| `catalog` | Passed as each notebook's `catalog` parameter. Default `rideflow_dev`. |
| `catalog_storage_root` | Managed location for a catalog setup creates. Blank uses the metastore's storage. |
| `landing_storage_root` | External storage for the landing Volumes. Blank uses managed Volumes. |
| `lakelogic_version`, `lakelogic_wheel`, `lakelogic_extras` | The LakeLogic install |

The jobs set `contracts_root` to `${workspace.file_path}/contracts` and `environment` to the bundle target. The bundle syncs `contracts/` into its workspace root.

The `catalog` variable alone does not rename the domain catalogs. Those names come from the registry settings above.

## Required permissions

To create a new catalog, the identity running setup needs metastore `CREATE CATALOG`. On a metastore with no default storage, setup also needs `catalog_storage_root`.

If you do not have that privilege:

1. Ask an administrator to create the `rideflow_dev_<domain>` catalogs.
2. Grant your identity permission to create schemas and Volumes inside them.
3. Run setup again.

Setup checks whether each catalog exists first. When it exists, setup adds the required schemas and Volumes.

## Verify the target before deployment

Authenticate with an explicit Databricks profile and verify the current identity:

```bash
databricks auth login --host https://<your-workspace>.azuredatabricks.net -p rideflow_dev
databricks -p rideflow_dev current-user me
```

Pass `-p rideflow_dev` to bundle commands or set `DATABRICKS_CONFIG_PROFILE=rideflow_dev`. Otherwise, the CLI may use the default profile and target a different workspace.

## Clean up renamed catalogs

Replace the default prefix in the deletion command:

```bash
for domain in business marketing marketplace operations payments reference shared; do
  databricks catalogs delete "<your-prefix>_${domain}" --force -p rideflow_dev
done
```

Catalog deletion does not remove bundle-managed jobs or synced workspace files. Run `databricks bundle destroy` separately when the Asset Bundle was deployed.

# Aster Communication Server — Product Overview

> Fictional internal documentation for a RAG demonstration. Product names, endpoints, credentials, and operating procedures in this collection are invented; do not apply them to a real service.

**Document owner:** Platform Engineering  
**Applies to:** Aster Communication Server (ACS) 2.3 and 2.4  
**Document ID:** ACS-OV-01

## Purpose and supported deployment

Aster Communication Server (ACS) routes internal notification events to registered applications. A supported production deployment contains one ACS application node and one external PostgreSQL database. This training product does not support active-active application nodes. ACS 2.3 and 2.4 are the only versions described in this documentation set.

The ACS application contains three logical components:

| Component | Responsibility | Operational name |
| --- | --- | --- |
| API Gateway | Accepts management requests and serves health endpoints | `acs-api` |
| Delivery Worker | Reads queued events and delivers notifications | `acs-worker` |
| Configuration Store | Holds tenants, routing rules, and delivery history in PostgreSQL | `acsdb` |

The API Gateway and Delivery Worker run under the `acs-server` systemd service. The external database is administered separately. Stopping `acs-server` stops both application components but does not stop PostgreSQL.

## Terms used in ACS procedures

- **Tenant:** A logical customer environment identified by a tenant ID, such as `tenant-orion`.
- **Delivery queue:** Pending notification events held in `acsdb`. An empty queue is required before a planned upgrade.
- **Maintenance mode:** An API setting that rejects new events while the worker finishes events already in the queue.
- **Full backup:** A consistent export of the ACS database plus a copy of the active `/etc/acs/acs.yaml` file. Copying the configuration file alone is not a full backup.

## Version selection and source of truth

Always identify the installed version before applying an operational procedure. Run `acsctl version` on the ACS node and record its complete output in the change record. If a question names ACS 2.3, use the sections explicitly labeled 2.3; if it names ACS 2.4, use the 2.4 sections. If no version is provided, ask for it before giving version-dependent instructions. The configuration and release notes documents record the effective version-specific values.

## Documentation map

- [Installation](installation.md): prerequisites, initial deployment, and health checks.
- [Configuration](configuration.md): ports, paths, configuration changes, and API behavior.
- [Backup and restore](backup-restore.md): version-specific backup and recovery procedures.
- [Troubleshooting](troubleshooting.md): symptoms and diagnostic decisions.
- [Release notes](release-notes.md): changes between ACS 2.3 and 2.4, including upgrade and rollback constraints.

For all operational procedures in this training collection, commands and addresses are examples for the fictional `acs.internal.example` environment. An unknown setting, feature, or version is not documented merely because it resembles a real product.

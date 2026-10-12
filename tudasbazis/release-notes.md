# Aster Communication Server — Release Notes and Upgrade Policy

> Fictional internal documentation for a RAG demonstration. Release details are invented.

**Document owner:** Release Engineering  
**Applies to:** ACS 2.3 and 2.4  
**Document ID:** ACS-RN-06

## ACS 2.3 — Baseline behavior

ACS 2.3 uses HTTPS port 8443 by default and retains completed delivery records for 30 days by default. All supported configuration changes require an `acs-server` restart. Full backups require stopping the application after maintenance mode is enabled and both queue counters reach 0. The maintenance endpoint is `POST /api/v1/maintenance/enable`.

## ACS 2.4 — Changes from 2.3

ACS 2.4 uses HTTPS port 9443 by default; port 8443 is not kept open automatically. Completed delivery records are retained for 45 days by default. Retention-only changes support `acsctl config reload` when the new value is an integer from 7 to 365; port, TLS, and database changes still require a restart. The maintenance endpoint changes to `POST /api/v2/maintenance/enable`. ACS 2.4 supports an online full backup only with an approved consistent PostgreSQL snapshot and WAL archiving enabled; otherwise take a stopped-application backup. The queue-status endpoint remains `GET /api/v1/queue/status`.

## Upgrade from ACS 2.3 to 2.4

This is the only upgrade path documented here. Reserve a maintenance window because the database schema migration and service restart interrupt availability. Perform these actions in order:

1. Confirm `acsctl version` reports ACS 2.3. Record the currently effective `api.listen_port`, including any explicit override in `/etc/acs/acs.yaml`.
2. Take a successful ACS 2.3 full backup using its stopped-application procedure in [Backup and restore](backup-restore.md); retain the versioned database export and matching configuration file off-node.
3. Enable ACS 2.3 maintenance mode and wait until `pendingEvents` and `inFlightEvents` are both 0. If maintenance remains enabled from the backup window, verify both counters again. Stop `acs-server`.
4. Apply the approved ACS 2.4 package and run the package's database migration procedure. Treat a migration failure as a failed upgrade; do not start an unverified mixed-version deployment.
5. Review `/etc/acs/acs.yaml`: an explicitly configured `api.listen_port` is preserved; without an override, update network access and monitoring to the new default port 9443.
6. Start `acs-server`, verify `acsctl version` reports 2.4, and check `/health/ready` for HTTP 200 on the effective port. Disable maintenance with `POST /api/v2/maintenance/disable` and verify normal event intake.

The backup step does not eliminate the need to drain the queue immediately before the actual upgrade; events may arrive between the two steps.

## Rollback after a 2.4 schema migration

The 2.4 schema migration has no documented reverse migration. For rollback, stop `acs-server`, reinstall the approved ACS 2.3 package, and restore the matching pre-upgrade ACS 2.3 database export and `/etc/acs/acs.yaml`. Verify readiness on the restored effective port before reopening event intake. Events accepted after the pre-upgrade backup are not present in the restored database; reconcile them through the organization's incident process. Do not simply install the 2.3 binary over a migrated 2.4 database.

## Unsupported or unspecified behavior

This collection does not document ACS 2.5, cross-version database restores, automated rollback, active-active nodes, backup retention duration, or disaster recovery targets. For these topics, request current product documentation rather than extrapolating from ACS 2.3 or 2.4.

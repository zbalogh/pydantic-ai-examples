# Aster Communication Server — Backup and Restore

> Fictional internal documentation for a RAG demonstration. Commands and backup formats are illustrative.

**Document owner:** Platform Engineering  
**Applies to:** ACS 2.3 and 2.4  
**Document ID:** ACS-BR-04

## Backup contents and naming

A full ACS backup contains a consistent export of PostgreSQL database `acsdb` and the active file `/etc/acs/acs.yaml`. Store the artifacts together under a change-specific location and record the ACS version, PostgreSQL version, creation time, and database host in a manifest. For example, a backup from an ACS 2.3 upgrade rehearsal might be named `acs-2.3-preupgrade-2026-09-28`. Backups must be copied to approved storage separate from the ACS node. A file copy of `/etc/acs/acs.yaml` without the database export is not sufficient for recovery.

## ACS 2.3 — Full backup requires a stopped application

ACS 2.3 does not support an online full backup. Plan an outage and follow this order:

1. Enable maintenance mode with `POST /api/v1/maintenance/enable` using an authenticated operator session.
2. Poll `GET /api/v1/queue/status` until both `pendingEvents` and `inFlightEvents` are 0.
3. Stop `acs-server` with `systemctl stop acs-server`.
4. Export `acsdb` with the organization's approved PostgreSQL 15 logical-backup procedure; copy `/etc/acs/acs.yaml` and write the backup manifest.
5. Start `acs-server`, confirm HTTP 200 at the version-appropriate `/health/ready` endpoint, then disable maintenance mode with `POST /api/v1/maintenance/disable`.

If either queue count does not reach 0, do not take the planned backup or stop the service. Escalate to the ACS operator; [Troubleshooting](troubleshooting.md) contains initial queue checks.

## ACS 2.4 — Supported online full backup

ACS 2.4 supports a full backup while `acs-server` remains running, but only when PostgreSQL 15 WAL archiving is enabled and the organization's approved backup process captures a consistent database snapshot together with the required WAL files. Copy `/etc/acs/acs.yaml` and include it in the same backup manifest. Check that the approved backup job reports a completed and recoverable snapshot before marking the backup successful. No maintenance mode or queue drain is required for this online procedure. If WAL archiving or a consistent snapshot is unavailable, use the stopped-application procedure below.

## ACS 2.4 — Stopped-application fallback

For a planned offline ACS 2.4 backup, enable maintenance with `POST /api/v2/maintenance/enable`; poll `GET /api/v1/queue/status` until `pendingEvents: 0` and `inFlightEvents: 0`; stop `acs-server`; export `acsdb` and copy `/etc/acs/acs.yaml`; restart the service; confirm readiness; then disable maintenance with `POST /api/v2/maintenance/disable`.

## Restore and version compatibility

Restore the database and its matching configuration file only into the same ACS version that created the backup. Stop `acs-server` first, restore both artifacts using approved database and file-recovery tooling, then start `acs-server` and verify HTTP 200 from `/health/ready`. Do not restore an ACS 2.3 database backup directly into a running ACS 2.4 instance. An ACS 2.4 upgrade changes the database schema; rollback requires reinstalling ACS 2.3 and restoring its pre-upgrade 2.3 backup as specified in [Release notes](release-notes.md). This set does not define retention periods, encryption keys, or database recovery tooling.

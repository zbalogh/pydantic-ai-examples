# Aster Communication Server — Troubleshooting Guide

> Fictional internal documentation for a RAG demonstration. Symptoms and procedures describe an invented product.

**Document owner:** Platform Engineering  
**Applies to:** ACS 2.3 and 2.4  
**Document ID:** ACS-TS-05

## First checks for any incident

Record the installed version with `acsctl version`, the configured `api.listen_port` from `/etc/acs/acs.yaml`, and the `acs-server` service state. If the port is not explicitly set, use 8443 for ACS 2.3 or 9443 for ACS 2.4. Record the HTTP status of `/health/live` and `/health/ready` on the effective HTTPS port. Collect service logs using `journalctl -u acs-server --since "15 minutes ago"`. Do not put passwords, session tokens, or private keys in an incident ticket.

## `/health/live` is 200 but `/health/ready` is 503

This combination means the API process responds but ACS is not ready to serve requests. Check connectivity from the ACS node to the external PostgreSQL 15 server on TCP 5432, verify the configured `database.host` and `database.name: acsdb`, and review the `acs-server` logs for database authentication or worker initialization failures. A readiness 503 does not prove that the database is the cause; investigate worker initialization if database connectivity succeeds. Do not disable the readiness check to make a failed deployment appear healthy.

## API unavailable immediately after upgrading to ACS 2.4

ACS 2.4 changes the default HTTPS management port from 8443 to 9443. First read the active `api.listen_port`; if no override exists, test `https://acs.internal.example:9443/health/ready` and check that the network policy permits TCP 9443. ACS 2.4 does not keep 8443 open as a compatibility listener. If `api.listen_port` is explicitly set, test its configured value instead. A connection failure on 8443 alone is not evidence of a failed 2.4 upgrade.

## Delivery queue does not drain before an ACS 2.3 backup or upgrade

After enabling maintenance with `POST /api/v1/maintenance/enable`, query `GET /api/v1/queue/status`. The service may still have events in flight after `pendingEvents` reaches 0. Wait until both `pendingEvents` and `inFlightEvents` are 0. If either count remains nonzero, check `acs-server` logs for repeated delivery failures and escalate; do not stop the service to force completion of a planned backup or upgrade. The ACS 2.4 online backup does not require queue drain when all its snapshot and WAL prerequisites are met.

## Retention change appears ineffective

On ACS 2.3, `notifications.retention_days` requires a scheduled `acs-server` restart; a reload is not supported. On ACS 2.4, a retention-only change can use `acsctl config reload`; ensure the new value is an integer from 7 to 365 and check the reload result. If a port, TLS, or database setting was also changed, restart in a maintenance window. A retention setting changes future cleanup behavior; it does not restore delivery records already deleted.

## Escalation evidence

Attach the ACS version, effective port, UTC observation time, health status codes, both queue counters where relevant, and redacted service log excerpts. If a symptom is not covered here, state that the guide has no documented diagnosis and escalate to Platform Engineering rather than inventing a recovery command.

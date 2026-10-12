# Aster Communication Server — Configuration Reference

> Fictional internal documentation for a RAG demonstration. All settings and URLs are invented.

**Document owner:** Platform Engineering  
**Applies to:** ACS 2.3 and 2.4  
**Document ID:** ACS-CF-03

## Active file and setting precedence

The active application configuration is `/etc/acs/acs.yaml`. Read the installed version with `acsctl version` before changing a setting. Explicit values in the active file take precedence over the version's default values below. Never infer the effective port solely from a release note when `api.listen_port` is set explicitly.

| Setting | ACS 2.3 default | ACS 2.4 default | Effect |
| --- | --- | --- | --- |
| `api.listen_port` | `8443` | `9443` | HTTPS management API and health endpoints |
| `notifications.retention_days` | `30` | `45` | Days to retain completed delivery records |
| `database.name` | `acsdb` | `acsdb` | PostgreSQL database name |
| `api.tls_cert_file` | `/etc/acs/tls/server.crt` | `/etc/acs/tls/server.crt` | Server certificate |
| `api.tls_key_file` | `/etc/acs/tls/server.key` | `/etc/acs/tls/server.key` | Matching private key |

These are application defaults, not proof that a running installation uses them. Example HTTPS host: `acs.internal.example`. The database server listens on TCP 5432 in this reference deployment.

## ACS 2.3 — Applying configuration changes

In ACS 2.3, changing `api.listen_port`, TLS file paths, database settings, or `notifications.retention_days` requires `systemctl restart acs-server`. Schedule a maintenance window before the restart: it interrupts API access and the Delivery Worker. Before restarting, use the maintenance API to stop new event intake and wait for the delivery queue to drain. Follow the procedure in [Backup and restore](backup-restore.md) if the change is part of a planned upgrade.

## ACS 2.4 — Applying configuration changes

In ACS 2.4, a change limited to `notifications.retention_days` can be applied with `acsctl config reload` without restarting `acs-server`. The reload validates the new value, which must be an integer from 7 through 365. If validation fails, the running value remains in effect and the operator must correct `/etc/acs/acs.yaml` before retrying. Changes to `api.listen_port`, TLS file paths, or database settings still require `systemctl restart acs-server` and a maintenance window. A mixed change that includes retention and any restart-only setting also requires a restart.

## Version-specific maintenance API

The maintenance API requires an authenticated operator session; its authentication setup is outside this documentation set. ACS 2.3 uses `POST /api/v1/maintenance/enable` and `POST /api/v1/maintenance/disable`. ACS 2.4 uses `POST /api/v2/maintenance/enable` and `POST /api/v2/maintenance/disable`. Both versions provide `GET /api/v1/queue/status`; the response field `pendingEvents` reports events waiting for delivery. Do not assume that `pendingEvents: 0` means no event is currently being processed; verify the `inFlightEvents` field is also 0 before stopping the service.

## Effective configuration example

For an ACS 2.4 installation with no explicit port or retention override, the API listens on TCP 9443 and completed delivery records are retained for 45 days. For an ACS 2.4 installation that explicitly sets `api.listen_port: 10443`, use 10443 for the API and readiness URL. The 2.3 default of 8443 is not an alternate listener in 2.4.

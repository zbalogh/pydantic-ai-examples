# Aster Communication Server — Installation and Initial Verification

> Fictional internal documentation for a RAG demonstration. Do not run these invented procedures against a real system.

**Document owner:** Platform Engineering  
**Applies to:** ACS 2.3 and 2.4  
**Document ID:** ACS-IN-02

## Supported layout and prerequisites

Install one ACS application node with 4 vCPU, 8 GiB RAM, and 40 GiB free space under `/var/lib/acs`. Provide a separately managed PostgreSQL 15 instance and a database named `acsdb`. This documentation does not define database installation or high availability. Reserve the internal DNS name `acs.internal.example` for the application node.

ACS requires outbound connectivity from the application node to PostgreSQL on TCP 5432. Operators reach the management API over HTTPS. The API port differs by version: ACS 2.3 defaults to TCP 8443; ACS 2.4 defaults to TCP 9443. See [Configuration](configuration.md) for the port and certificate settings.

## Installation sequence

1. Confirm that PostgreSQL 15 is reachable and `acsdb` exists. Record the database host in the deployment record.
2. Install the ACS package matching the target version using the organization's approved package process. The package identifier used in this fictional environment is `acs-server`.
3. Populate `/etc/acs/acs.yaml` with `database.host`, `database.name`, and TLS certificate paths. Set `api.listen_port` only if the deployment requires a nondefault port. Store the database password in the organization's secret store; this document does not specify a password or secret-store integration.
4. Start the application with `systemctl start acs-server`. Starting the service starts the API Gateway and Delivery Worker together.
5. Query the version-appropriate readiness endpoint. ACS 2.3: `https://acs.internal.example:8443/health/ready`. ACS 2.4: `https://acs.internal.example:9443/health/ready`.

The readiness endpoint returns HTTP 200 when the application can connect to `acsdb` and the worker has initialized. HTTP 503 means the node is not ready; it does not, by itself, identify the cause. The liveness endpoint `/health/live` only confirms that the API process is responsive and does not establish database readiness.

## Initial verification record

Record the output of `acsctl version`, the readiness status, and the effective `api.listen_port` in the installation ticket. The expected default ports are 8443 for ACS 2.3 and 9443 for ACS 2.4. A customized `api.listen_port` takes precedence over the default; use the configured port when testing health or API access.

## Installation boundaries

ACS 2.4 can be installed as a new deployment or reached by upgrading ACS 2.3. An upgrade is governed by the [Release notes](release-notes.md) and must not be treated as a fresh installation. ACS 2.2, clustered application nodes, and automatic database provisioning are outside this documentation set.

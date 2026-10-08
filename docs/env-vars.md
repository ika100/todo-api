# Environment variables

Configuration is read exclusively from environment variables. Defaults below are the application defaults. The deployed values are set per environment in the product's gitops-app repo (`services.yaml` → `env`, `replicas`, `resources`).

## Core

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8080` | HTTP port the service listens on. |
| `LOG_LEVEL` | `INFO` | Logging level. One of `DEBUG`, `INFO`, `WARNING`, `ERROR`. |

## Observability

| Variable | Default | Description |
|---|---|---|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _(unset — tracing disabled)_ | Standard OpenTelemetry endpoint, e.g. `http://otel-collector:4318`; injected by the platform's observability addon. When set, `configure_tracing()` runs at startup. |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `http/protobuf` | `http/protobuf` or `grpc`. |
| `OTEL_SERVICE_NAME`, `OTEL_RESOURCE_ATTRIBUTES` | _(project name)_ | Resource attributes; set by the observability addon. |
| `OTLP_ENDPOINT` | _(unset)_ | Legacy gRPC endpoint (kept for compatibility); prefer the standard variables. |
| `METRICS_PORT` | `8080` | Port serving `/metrics` (same as the main HTTP port unless overridden). |

## Database

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | _(none, required)_ | Postgres connection URL, e.g. `postgresql://user:password@host:5432/db`. Startup fails if unset. In the cluster it is injected by the postgres addon (`uses: [postgres]`) from Secret `todo-postgres-app`. The `todos` table is created automatically at startup. |
| `TEST_DATABASE_URL` | _(unset)_ | Tests only. Use this Postgres instead of starting a testcontainer. |

The addon also injects the standard `PG*` variables (`PGHOST`, `PGUSER`, ...); the service does not read them.

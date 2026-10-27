# Architecture and operations

The local adapter assigns each point to a fixed-size geographic cell. A query calculates a conservative cell neighborhood, loads only candidates, evaluates exact great-circle distance, filters by radius, and sorts by `(distance, id)` for deterministic output.

The grid is intentionally understandable rather than globally optimal: longitude degree width changes by latitude and polar workloads need special handling. Production adapters can use PostGIS GiST indexes or H3 cells while retaining the HTTP contract.

## Production topology

Keep API processes stateless and use PostGIS as the source of truth. Stream bulk imports into a queue, validate asynchronously, and publish an ingestion status resource. Cache only popular immutable query shapes. Partition by tenant or region after observing skew, not pre-emptively.

Track p50/p95/p99 query latency, candidates scanned, rejected coordinates, batch size, index lag, and result cardinality.

## Twelve-factor mapping

| Factor | Implementation |
|---|---|
| Codebase | One geospatial API repository |
| Dependencies | Declared Python package and pinned CI environment |
| Config | Cell size, batch limits, port, and store URL use environment variables |
| Backing services | Spatial database/cache are attached resources |
| Build, release, run | CI, image build, and runtime configuration are separate |
| Processes | Durable points live externally in production; APIs are stateless |
| Port binding | Uvicorn exports HTTP directly |
| Concurrency | Horizontal APIs and partitioned ingestion workers |
| Disposability | Bounded batches and idempotent ingestion IDs support restarts |
| Dev/prod parity | Same package and API with local or PostGIS adapters |
| Logs | Structured request and ingestion events stream outward |
| Admin processes | Reindex/backfill jobs run from the same release |

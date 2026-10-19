# Architecture Index

This index is not the full contract. Do not implement from this file alone; follow the artifact paths below.

## Implementation Guide

### Global artifacts
- `unit_graph.yaml`
  - who reads: all implementation workers
  - use for: unit boundary, entrypoints, dependencies, exported signatures, shared refs
  - how to consume: find the assigned unit and follow its source anchors and shared_refs
- `migration_boundary.yaml`
  - who reads: all implementation workers
  - use for: rewrite scope and runtime boundary
  - how to consume: read `must_rewrite` before changing code; `source_anchors` are not rewrite targets
- `wire_contracts.yaml`
  - who reads: workers touching REST/API code
  - use for: request/response/error contracts and semantic divergence
  - how to read: filter rows by `unit` or `global`
- `shared_modules.yaml`
  - who reads: workers whose unit touches shared domain models or security helpers
  - use for: god-class awareness and migration strategy
  - how to read: filter rows by `used_by_units`
- `cross_unit_state.yaml`
  - who reads: workers depending on token/session flows
  - use for: session/local storage and implicit shared state
  - how to read: filter rows where `writer.unit` or `reader.unit` matches the assigned unit

### Unit: cliente-cadastro
- external trigger: API `POST /api/clientes`
- must read:
  - `units/cliente-cadastro/behavior.yaml`
  - `units/cliente-cadastro/bindings.yaml`
  - `units/cliente-cadastro/unit_decomposition.yaml`
- relevant global rows:
  - `wire_contracts.yaml` rows for `cliente-cadastro`
  - `shared_modules.yaml` rows where `used_by_units` includes `cliente-cadastro`
  - `cross_unit_state.yaml` flows touching `cliente-cadastro`
- before DONE report: artifacts_read, implemented_must_preserve, unresolved_or_deferred, verification evidence

### Unit: cliente-login
- external trigger: API `POST /api/auth/login`
- must read:
  - `units/cliente-login/behavior.yaml`
  - `units/cliente-login/bindings.yaml`
  - `units/cliente-login/unit_decomposition.yaml`
- relevant global rows:
  - `wire_contracts.yaml` rows for `cliente-login`
  - `shared_modules.yaml` rows where `used_by_units` includes `cliente-login`
  - `cross_unit_state.yaml` flows touching `cliente-login`
- before DONE report: artifacts_read, implemented_must_preserve, unresolved_or_deferred, verification evidence

### Unit: cliente-recuperacao
- external trigger: API `POST /api/auth/solicitar-recuperacao` and `POST /api/auth/redefinir-senha`
- must read:
  - `units/cliente-recuperacao/behavior.yaml`
  - `units/cliente-recuperacao/bindings.yaml`
  - `units/cliente-recuperacao/unit_decomposition.yaml`
- relevant global rows:
  - `wire_contracts.yaml` rows for `cliente-recuperacao`
  - `shared_modules.yaml` rows where `used_by_units` includes `cliente-recuperacao`
- before DONE report: artifacts_read, implemented_must_preserve, unresolved_or_deferred, verification evidence

### Unit: cliente-perfil
- external trigger: API `GET/PUT /api/perfil`
- must read:
  - `units/cliente-perfil/behavior.yaml`
  - `units/cliente-perfil/bindings.yaml`
  - `units/cliente-perfil/unit_decomposition.yaml`
- relevant global rows:
  - `wire_contracts.yaml` rows for `cliente-perfil`
  - `shared_modules.yaml` rows where `used_by_units` includes `cliente-perfil`
  - `cross_unit_state.yaml` flows touching `cliente-perfil`
- before DONE report: artifacts_read, implemented_must_preserve, unresolved_or_deferred, verification evidence

### Unit: produto-admin
- external trigger: API `GET/POST/PUT/DELETE /api/produtos`
- must read:
  - `units/produto-admin/behavior.yaml`
  - `units/produto-admin/bindings.yaml`
  - `units/produto-admin/unit_decomposition.yaml`
- relevant global rows:
  - `wire_contracts.yaml` rows for `produto-admin`
  - `shared_modules.yaml` rows where `used_by_units` includes `produto-admin`
- before DONE report: artifacts_read, implemented_must_preserve, unresolved_or_deferred, verification evidence

### Unit: admin-login
- external trigger: API `POST /api/admin/auth/login`
- must read:
  - `units/admin-login/behavior.yaml`
  - `units/admin-login/bindings.yaml`
  - `units/admin-login/unit_decomposition.yaml`
- relevant global rows:
  - `wire_contracts.yaml` rows for `admin-login`
  - `shared_modules.yaml` rows where `used_by_units` includes `admin-login`
- before DONE report: artifacts_read, implemented_must_preserve, unresolved_or_deferred, verification evidence

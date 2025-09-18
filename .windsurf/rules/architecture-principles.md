---
trigger: always_on
---

---
trigger: always_on
---

# Architecture Principles

## Folder Responsibilities
- `/domain/`
  - Contains entities, value objects, aggregates, domain services.
  - Contains only business rules — no frameworks, DB, or external code.
  - Must not import from other layers.

- `/application/`
  - Contains use cases, application services, orchestration.
  - Coordinates domain objects and infrastructure.
  - May depend on domain, but never directly on infrastructure.
  - No business rules here — only workflow logic.

- `/interfaces/`
  - Entry points: REST controllers, CLI, gRPC, message consumers.
  - Translate external input/output into application calls.
  - May depend on application layer only.

- `/infrastructure/`
  - Implementations of repositories, database connectors, API clients.
  - May depend on domain (to implement repository interfaces).
  - No business rules here.

- `/shared/`
  - Cross-cutting concerns: logging, config, auth, error handling.
  - Must not contain domain or application logic.

- `/utils/`
  - Generic helper functions with no domain knowledge.
  - Keep minimal — prefer placing code in domain/application if relevant.

## Dependencies Rules
- Dependencies flow inward: interfaces → application → domain.  
- Infrastructure depends inward, never outward.  
- Domain is the core and must never depend on application, infrastructure, or interfaces.  
- Shared code must be generic and reusable.  
- Utils must be pure helpers with no side effects on architecture.

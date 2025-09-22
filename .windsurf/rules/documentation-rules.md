---
trigger: manual
---

---
trigger: manual
---

# Documentation

## Documentation Structure
- `/docs/architecture.md` — high-level diagram of domain, application, interfaces, infrastructure layers.
- `/docs/domain/` — describe entities, aggregates, value objects.
- `/docs/use_cases.md` — describe application workflows and dependencies.
- `/docs/interfaces/` — describe API endpoints, CLI commands, or message formats.
- `/docs/infrastructure/` — describe databases, repositories, external integrations.
- `/docs/shared.md` — describe cross-cutting concerns (config, logging, etc.).
- `/docs/sphinx/_build/markdown/markdown/` — sphinx-generated module and function documentation (read-only).

## Documentation Update
- When a new domain object is created, update `/docs/domain/`.
- When a new use case is added, update `/docs/use_cases.md`.
- When a new API is added, update `/docs/interfaces/`.
- When infrastructure is changed, update `/docs/infrastructure/`.

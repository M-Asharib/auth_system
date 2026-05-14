# GitHub Actions Workflow Tasks

## Stage 1: Runner & Service Orchestration
- [x] Define `pipeline.yml` with `ubuntu-latest` runners.
- [x] Configure `jobs.services` with:
    - **PostgreSQL**: Latest version with async-ready config.
    - **Redis**: Fast memory layer container.
- [x] Implement **Wait-for-Service** scripts (via Docker health checks).

## Stage 2: Quality Engine (Linter)
- [x] Setup `Python` environment with cached dependencies.
- [x] Run `Flake8` or `Ruff` to assert:
    - Zero syntax errors.
    - Zero unused references.
    - Strict adherence to PEP8 standards.

## Stage 3: SAST Security Audits
- [x] Integrate `Bandit` scan for the source directory.
- [x] Configure build failure if:
    - Hardcoded credentials are detected.
    - Weak cryptography bindings (algorithms other than HS256) are found.
    - Dangerous function calls are used.

## Stage 4: Execution & Integration Suites
- [x] Execute `Pytest` targeting all endpoints.
- [x] Assert 100% pass rate for:
    - Registration persistence.
    - Dual-token (Access/Refresh) generation.
    - Redis-based blacklist lockout verification.
- [x] Ensure non-blocking network call patterns are verified.

## Stage 5: Compliance Gate
- [ ] Implement `Branch Protection` logic via status checks.
- [ ] Block merges if any component of the pipeline returns a non-zero exit code.
- [ ] Generate a `Compliance Report` artifact upon successful completion.

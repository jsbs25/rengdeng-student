# Project Audit: rengdeng-student

## Executive summary

This repository is a working prototype for an Arabic-learning platform with three delivery surfaces:

- Web app served by `server.py`
- Expo/React Native app under `app/`
- WeChat mini-program under `miniprogram/`

The project is feature-rich and demonstrates a credible product roadmap, but it is not yet in a production-grade engineering state. The main risks are concentration of business logic in monolithic scripts, weakly enforced security boundaries, and incomplete CI/test coverage.

This is best described as a prototype-to-product codebase that needs hardening before public production use or enterprise-grade deployment.

## Scope reviewed

- `README.md`
- `.github/workflows/ci.yml`
- `.gitignore`
- `server.py`
- `app/electron/server.py`
- `app/src/config.js` and related app config files (as represented in repository structure)
- mini-program and app docs

## Current architecture

### 1) Monolithic backend

The primary backend is a single Python HTTP server in `server.py` that serves:

- static HTML/JS/CSS files
- `/api/books`
- `/api/articles`
- `/api/vocab`
- `/api/sentences`
- `/api/chat/message`

This configuration is practical for rapid iteration, but it couples:

- web serving
- API routing
- AI gateway integration
- content serving
- session access patterns
- static asset delivery

The code is therefore difficult to reason about, secure, and evolve.

### 2) Multi-client delivery model

The repository supports multiple clients that all connect to the same backend:

- web frontend (`arabic_learning.html` and generated assets)
- Expo app (`app/`)
- WeChat mini-program (`miniprogram/`)

This architecture is viable, but it increases the need for:

- consistent API contracts
- safer auth/session handling
- environment isolation
- versioned data access rules

### 3) Asset-heavy data model

Large content sets are stored under `data/` and embedded in the app, including:

- books
- articles
- classroom-like sentence banks
- Quran and library data
- generated caches and large page analysis artifacts

This is useful for offline use and local deployment, but it also introduces operational and maintenance risks, especially when data is centrally embedded in both generated static pages and runtime APIs.

## Key findings

### Finding 1: Security policy is not fully enforced

Evidence:

- `server.py` sets `Access-Control-Allow-Origin: *` in HTTP responses.
- `app/electron/server.py` does the same.
- code reads credentials from local files and environment variables, including:
  - `data/ai_key.txt`
  - `DEEPSEEK_API_KEY`
  - `NUR_AI_URL`
  - `LOBSTER_APIKEY_DEEPSEEK`

Observations:

- This is acceptable for a local prototype, but it is not a robust production pattern.
- A permissive CORS configuration can expose browser-origin attack surfaces if the backend is ever used more broadly.
- Secret loading is not centralized and is not strictly environment-isolated.

Risk: medium

### Finding 2: Sensitive data is partially protected, but not all critical flows are governed

Evidence:

- `.gitignore` already includes obvious secret and runtime files such as:
  - `data/users.json`
  - `data/codes.json`
  - `data/pays.json`
  - `data/unlocks.json`
  - `data/secret.txt`
  - `data/ai_key.txt`
  - `.env`

This is a good start, but it is not a complete security baseline.

Observations:

- The project contains many generated data files and cache directories that are large and may include sensitive user or content-derived material.
- The repository still contains multiple files and folders that reflect local runtime state, not necessarily production-safe artifacts.
- There is no clear separation between “source content,” “user state,” and “secret/credential environment.”

Risk: medium

### Finding 3: CI is too lightweight for the risk profile

Evidence:

- `.github/workflows/ci.yml` only runs:
  - `python3 -m py_compile server.py admin_panel.py build_home.py openiti_stream.py`
  - `python3 tools/verify_web.py`

Observations:

- This validates syntax and a web smoke check, but it does not cover:
  - API integration tests
  - security regression checks
  - data validation
  - authentication flows
  - external AI endpoint failures
  - cross-client compatibility

Risk: medium

### Finding 4: AI integration is convenient but loosely governed

Evidence:

- `server.py` and `app/electron/server.py` contain fallback logic for DeepSeek and local AI endpoints.
- AI endpoints are auto-discovered from local application configuration and common localhost ports.

Observations:

- This supports local experimentation and dev usage well.
- It creates inconsistent environment assumptions between repository, local machine, and deployment environment.
- Production hosting should define a single, explicit AI configuration model and validate it at startup.

Risk: medium

### Finding 5: Data access and persistence are not yet structured for production

Evidence:

- README explicitly describes data as “embedded offline available” and generated artifacts under `data/`.
- Several datasets are large and generated.
- There are no clear database boundaries for user state, subscriptions, or runtime session records.

Observations:

- This is acceptable in an early product prototype, but it is not robust enough for multi-user production deployment.
- User-sensitive fields, metrics, and subscription state need explicit governance.

Risk: medium-high

## Positive observations

### Strong product momentum

The repository demonstrates strong product ambition:

- web app
- mini-program
- mobile app
- AI tutoring
- content library
- vocabulary system
- SRS/review logic
- daily learning paths
- generated static platform assets

This is not a toy experiment; it is a portfolio-grade product prototype.

### Good baseline hygiene in some areas

- `.gitignore` includes a meaningful set of secret paths.
- CI exists and is active.
- `tools/verify_web.py` and syntax checks provide some protection.
- README accurately documents product surface areas.

## Recommended remediation order

### Phase 1: security foundations

1. Centralize secret management behind environment-based configuration.
2. Replace wildcard CORS with a restricted allowlist strategy.
3. Separate user data, credentials, and content data into explicit directories or storage layers.
4. Define a clear deployment environment matrix: local, staging, production.

### Phase 2: backend modularization

1. Extract API route handlers from `server.py` into modules.
2. Isolate AI provider code from HTTP routing.
3. Define a stable response schema for `/api/*` endpoints.
4. Add startup validation for required config and content artifacts.

### Phase 3: resilience and testing

1. Add integration tests for endpoint health and JSON schema.
2. Add contract tests for mobile/web mini-program compatibility.
3. Add failure-path tests for AI provider quota, timeouts, and empty responses.
4. Add basic authentication/authorization tests to establish safe defaults.

### Phase 4: data governance

1. Move user state into a real database or a clearly versioned persistence layer.
2. Keep generated content in a separate artifact pipeline from user data.
3. Add backup/restore and migration discipline for large datasets.

### Phase 5: deployment hardening

1. Add production deployment checks before release.
2. Implement rate limiting and abuse controls.
3. Add error reporting and monitoring for API and content endpoints.
4. Define rollback and maintenance procedures for live deployment.

## Overall assessment

Status: viable prototype, not yet production-secure

The codebase is materially strong in idea and feature coverage, but it still needs:

- explicit security controls
- better backend structure
- more robust CI and tests
- clearer data governance
- production deployment guardrails

This project should be treated as a product prototype with clear engineering debt, not a final production platform.

## Suggested next step

The most valuable next move is to create a controlled hardening branch and perform a first-pass refactor that:

1. isolates AI provider logic,
2. centralizes secrets,
3. restricts CORS,
4. adds endpoint-level tests,
5. keeps the existing product behavior stable while the architecture is modernized.

This is the safest path to move from prototype to deployable product without breaking client integrations.

## Evidence highlights

- `server.py` uses permissive CORS and reads local secret files.
- `app/electron/server.py` mirrors the same pattern.
- `.github/workflows/ci.yml` lacks meaningful production-level validation.
- `.gitignore` acknowledges secrets but does not guarantee end-to-end secret governance.

## Conclusion

The repository is promising and product-rich, but a disciplined hardening phase is required before public or commercial deployment. The highest priorities are security tightening, backend modularization, and stronger automated validation.

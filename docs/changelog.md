# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [1.0.1] — 2026-03-21

### Fixed

- `DonationsAPI` — replaced fake `/donations/` endpoint with real data sources (post `donators` + subscriber `payments`)
- Removed obsolete `Donation` model
- Fixed YAML `on` parsed as boolean in mkdocs docs
- Removed unused CLI module

## [1.0.0] — 2026-03-21

### Added

- `BoostyClient` — main async facade with context manager
- `SyncBoostyClient` — synchronous wrapper for non-async code (scripts, Django, Jupyter)
- Authentication: `AuthManager` with auto-refresh (`device_os=web`), `FileTokenStorage`, `MemoryTokenStorage`, `EnvTokenStorage`
- Configuration: `BoostySettings` with env vars, TOML, and programmatic overrides
- HTTP transport: browser-like headers, retry with exponential backoff, token-bucket rate limiter, middleware pipeline
- **Caching**: `MemoryCache` with TTL, `NullCache`, `CacheManager` with JSON serialization, pluggable `CacheBackend` protocol
- API modules:
  - `UsersAPI` — current user
  - `BlogsAPI` — blog info, blacklist
  - `PostsAPI` — two-step draft→publish flow, list, get, update, delete
  - `CommentsAPI` — read, create, delete, reply (with `int_id` for threading)
  - `SubscriptionsAPI` — levels CRUD, subscriber list with **email and payments** (`Subscriber` model), verification
  - `DonationsAPI` — donation data from posts (`donators`) and subscriber payments
  - `TargetsAPI` — money and subscriber goals (create, read, delete)
  - `ShowcaseAPI` — showcase items
  - `MediaAPI` — file, image, video, audio uploads
  - `BundlesAPI` — bundle management
- `PostBuilder` — fluent API for post creation with access control
- `Subscriber` model — typed model with `email`, `payments`, `status`, `on_time`, `off_time`, `is_active`, `is_paid`
- Event system: `EventPoller` with **real detectors** (new subscribers, cancellations, new comments), `EventDispatcher` with `@client.on()` decorator
- Models: `User`, `Blog`, `Post`, `PostTag`, `Comment`, `SubscriptionLevel`, `SubscriptionStatus`, `Subscriber`, `MediaFile`, `Target`, `PaginatedResponse[T]`
- Exception hierarchy: `BoostyAuthError`, `BoostyForbiddenError`, `BoostyNotFoundError`, `BoostyRateLimitError`, `BoostyServerError`, `BoostyNetworkError`
- Pagination: manual and async iterator support
- PEP 561 `py.typed` marker
- 90 tests (unit + integration + E2E against real Boosty API)
- Full documentation (MkDocs Material) with 23+ pages

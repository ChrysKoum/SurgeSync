# Requirements Document - SpecSync Bridge

## Introduction

SpecSync Bridge extends SpecSync to synchronize API contracts between multiple repositories (frontend, backend, microservices). It enables automatic detection of contract changes and keeps all services aligned without requiring a shared parent folder.

## Glossary

- **Bridge**: The cross-repository contract synchronization feature
- **Contract**: A formal specification of an API (endpoints, models, parameters)
- **Provider**: A repository that provides an API (e.g., backend, auth-service)
- **Consumer**: A repository that consumes an API (e.g., frontend, mobile)
- **Contract Cache**: Local copy of a dependency's contract stored in `.kiro/contracts/`
- **Sync**: The process of updating local contract caches from dependencies
- **Drift**: Mismatch between what a consumer expects and what a provider offers

## Requirements

### Requirement 1

**User Story:** As a backend developer, I want to automatically publish my API contract, so that frontend developers know what endpoints are available.

#### Acceptance Criteria

1. WHEN a backend developer commits code with API endpoints, THE Bridge SHALL extract the contract from the code
2. WHEN the contract is extracted, THE Bridge SHALL save it to `.kiro/contracts/provided-api.yaml`
3. WHEN the contract file is saved, THE Bridge SHALL include all endpoints with their methods, paths, parameters, and response types
4. WHEN the contract is updated, THE Bridge SHALL include a timestamp of the last update
5. WHEN multiple files contain endpoints, THE Bridge SHALL aggregate all endpoints into a single contract

### Requirement 2

**User Story:** As a frontend developer, I want to sync the backend's API contract, so that I know what endpoints I can call.

#### Acceptance Criteria

1. WHEN a frontend developer runs sync, THE Bridge SHALL fetch the backend's contract from its repository
2. WHEN the contract is fetched, THE Bridge SHALL save it to `.kiro/contracts/backend-api.yaml`
3. WHEN the local cache is updated, THE Bridge SHALL show what changed since the last sync
4. WHEN the backend repository is not accessible, THE Bridge SHALL use the cached contract and show a warning
5. WHEN sync completes, THE Bridge SHALL report the number of endpoints available

### Requirement 3

**User Story:** As a frontend developer, I want to detect when I'm calling endpoints that don't exist, so that I can fix integration issues before deployment.

#### Acceptance Criteria

1. WHEN frontend code calls an API endpoint, THE Bridge SHALL check if the endpoint exists in the cached backend contract
2. WHEN an endpoint is not found in the contract, THE Bridge SHALL flag it as drift
3. WHEN drift is detected, THE Bridge SHALL show the endpoint path and method that doesn't exist
4. WHEN drift is detected, THE Bridge SHALL suggest either updating the contract or removing the API call
5. WHEN all API calls match the contract, THE Bridge SHALL report successful alignment

### Requirement 4

**User Story:** As a backend developer, I want to know which endpoints frontend is using, so that I don't break their code when making changes.

#### Acceptance Criteria

1. WHEN frontend syncs the backend contract, THE Bridge SHALL record which endpoints frontend expects
2. WHEN frontend code uses an endpoint, THE Bridge SHALL track the usage location (file and line number)
3. WHEN backend changes an endpoint, THE Bridge SHALL check if any consumers are using it
4. WHEN a used endpoint is modified or removed, THE Bridge SHALL warn the backend developer
5. WHEN an endpoint has no consumers, THE Bridge SHALL mark it as potentially removable

### Requirement 5

**User Story:** As a developer, I want to configure which repositories my project depends on, so that Bridge knows where to sync contracts from.

#### Acceptance Criteria

1. WHEN a developer initializes Bridge, THE Bridge SHALL create `.kiro/settings/bridge.json`
2. WHEN adding a dependency, THE Bridge SHALL store the repository URL and contract path
3. WHEN the configuration is saved, THE Bridge SHALL validate that required fields are present
4. WHEN multiple dependencies are configured, THE Bridge SHALL support syncing from all of them
5. WHEN a dependency is removed, THE Bridge SHALL delete the cached contract

### Requirement 6

**User Story:** As a developer, I want Bridge to work without a shared parent folder, so that I can use it with repos in different locations.

#### Acceptance Criteria

1. WHEN repositories are in different folders, THE Bridge SHALL sync contracts via git clone/pull
2. WHEN a contract is synced, THE Bridge SHALL use a temporary directory for git operations
3. WHEN the sync completes, THE Bridge SHALL clean up temporary files
4. WHEN git operations fail, THE Bridge SHALL provide clear error messages
5. WHEN working offline, THE Bridge SHALL use cached contracts and show a warning

### Requirement 7

**User Story:** As a developer working with microservices, I want to sync contracts from multiple services, so that I can validate all my dependencies.

#### Acceptance Criteria

1. WHEN multiple dependencies are configured, THE Bridge SHALL sync all contracts in parallel
2. WHEN syncing multiple contracts, THE Bridge SHALL show progress for each dependency
3. WHEN one sync fails, THE Bridge SHALL continue syncing other dependencies
4. WHEN all syncs complete, THE Bridge SHALL report success/failure for each dependency
5. WHEN contracts are synced, THE Bridge SHALL validate against all of them

### Requirement 8

**User Story:** As a developer, I want simple CLI commands to manage Bridge, so that I can easily sync and validate contracts.

#### Acceptance Criteria

1. WHEN running `specsync bridge init`, THE Bridge SHALL create the configuration file
2. WHEN running `specsync bridge add-dependency`, THE Bridge SHALL add a new dependency to the configuration
3. WHEN running `specsync bridge sync`, THE Bridge SHALL sync all configured dependencies
4. WHEN running `specsync bridge validate`, THE Bridge SHALL check for contract drift
5. WHEN running `specsync bridge status`, THE Bridge SHALL show the state of all dependencies

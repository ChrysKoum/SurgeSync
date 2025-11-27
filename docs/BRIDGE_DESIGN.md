# SpecSync Bridge - Decentralized Design

## Core Concept

Each repository stores contract information about **other repos it depends on** in its own `.kiro/` directory. No shared parent folder required.

## Architecture: Decentralized Contract Storage

```
frontend-repo/
├── .kiro/
│   ├── contracts/
│   │   ├── backend-api.yaml      ← What frontend expects from backend
│   │   └── auth-api.yaml         ← What frontend expects from auth service
│   └── settings/
│       └── bridge.json           ← Configuration

backend-repo/
├── .kiro/
│   ├── contracts/
│   │   ├── provided-api.yaml     ← What backend provides
│   │   └── auth-api.yaml         ← What backend expects from auth service
│   └── settings/
│       └── bridge.json

auth-service-repo/
├── .kiro/
│   ├── contracts/
│   │   └── provided-api.yaml     ← What auth service provides
│   └── settings/
│       └── bridge.json
```

**Key Insight:** Each repo only stores contracts for services it **directly interacts with**.

---

## Configuration Per Repo

### Frontend Configuration

```json
// frontend/.kiro/settings/bridge.json
{
  "bridge": {
    "enabled": true,
    "role": "consumer",
    "repo_id": "frontend",
    
    "dependencies": {
      "backend": {
        "type": "http-api",
        "sync_method": "git",
        "git_url": "https://github.com/myorg/backend.git",
        "contract_path": ".kiro/contracts/provided-api.yaml",
        "local_cache": ".kiro/contracts/backend-api.yaml",
        "sync_on_commit": true
      },
      "auth-service": {
        "type": "http-api",
        "sync_method": "git",
        "git_url": "https://github.com/myorg/auth-service.git",
        "contract_path": ".kiro/contracts/provided-api.yaml",
        "local_cache": ".kiro/contracts/auth-api.yaml",
        "sync_on_commit": true
      }
    },
    
    "extract_from": [
      "src/**/*.ts",
      "src/**/*.tsx"
    ],
    
    "api_patterns": [
      "api.get",
      "api.post",
      "fetch"
    ]
  }
}
```

### Backend Configuration

```json
// backend/.kiro/settings/bridge.json
{
  "bridge": {
    "enabled": true,
    "role": "provider",
    "repo_id": "backend",
    
    "provides": {
      "contract_file": ".kiro/contracts/provided-api.yaml",
      "extract_from": [
        "backend/handlers/**/*.py",
        "backend/models.py"
      ],
      "auto_update": true
    },
    
    "dependencies": {
      "auth-service": {
        "type": "http-api",
        "sync_method": "git",
        "git_url": "https://github.com/myorg/auth-service.git",
        "contract_path": ".kiro/contracts/provided-api.yaml",
        "local_cache": ".kiro/contracts/auth-api.yaml",
        "sync_on_commit": true
      }
    },
    
    "consumers": [
      {
        "repo_id": "frontend",
        "git_url": "https://github.com/myorg/frontend.git",
        "notify_on_change": true
      },
      {
        "repo_id": "mobile",
        "git_url": "https://github.com/myorg/mobile.git",
        "notify_on_change": true
      }
    ]
  }
}
```

---

## How It Works

### Scenario 1: Frontend Adds New API Call

**Step 1: Frontend Developer Commits**

```typescript
// frontend/src/api/users.ts
const posts = await api.get(`/users/${userId}/posts`);  // NEW
```

```bash
cd frontend
git commit -m "Add user posts feature"
```

**Step 2: SpecSync Bridge Detects Change**

```
🌉 SpecSync Bridge

Analyzing frontend commit...

New API call detected:
  GET /users/{userId}/posts

Checking backend contract...
  Loading: .kiro/contracts/backend-api.yaml
  
❌ Endpoint not found in backend contract

Would you like to:
  1. Update local expectation (create request)
  2. Check if backend has updated (sync now)
  3. Ignore this endpoint
```

**Step 3: Update Local Contract**

```yaml
# frontend/.kiro/contracts/backend-api.yaml
endpoints:
  - path: "/users/{id}/posts"
    method: GET
    status: expected  # Frontend expects this
    requested_by: frontend
    requested_at: "2024-11-27T14:00:00Z"
    response:
      type: array
      items: Post
```

**Step 4: Notify Backend (via Git)**

SpecSync creates a notification file:

```yaml
# frontend/.kiro/bridge/notifications/backend-request-001.yaml
from: frontend
to: backend
type: endpoint-request
timestamp: "2024-11-27T14:00:00Z"

request:
  endpoint: GET /users/{id}/posts
  reason: "User posts feature"
  expected_response:
    type: array
    items: Post
```

Then either:
- **Option A:** Push to a shared branch
- **Option B:** Create GitHub issue automatically
- **Option C:** Send webhook to backend repo

---

### Scenario 2: Backend Implements Endpoint

**Step 1: Backend Developer Commits**

```python
# backend/handlers/user.py
@app.get("/users/{id}/posts")
def get_user_posts(id: int) -> List[Post]:
    return db.get_posts_by_user(id)
```

```bash
cd backend
git commit -m "Implement user posts endpoint"
```

**Step 2: SpecSync Updates Contract**

```yaml
# backend/.kiro/contracts/provided-api.yaml
endpoints:
  - path: "/users/{id}/posts"
    method: GET
    status: implemented  # Now implemented
    implemented_at: "2024-11-27T15:00:00Z"
    response:
      type: array
      items:
        type: object
        fields:
          id: integer
          title: string
          content: string
```

**Step 3: Notify Consumers**

SpecSync creates notification:

```yaml
# backend/.kiro/bridge/notifications/frontend-update-001.yaml
from: backend
to: frontend
type: endpoint-implemented
timestamp: "2024-11-27T15:00:00Z"

update:
  endpoint: GET /users/{id}/posts
  status: implemented
  contract_url: "https://github.com/myorg/backend/blob/main/.kiro/contracts/provided-api.yaml"
```

**Step 4: Frontend Syncs**

```bash
cd frontend
git pull  # Or run: specsync bridge sync

🌉 SpecSync Bridge

Syncing contracts from dependencies...

✓ backend: 1 update available
  - GET /users/{id}/posts is now implemented
  
Updating local cache...
✓ .kiro/contracts/backend-api.yaml updated

Your API call will now work! 🎉
```

---

## Sync Methods

### Method 1: Git-Based Sync (Recommended)

Each repo commits its contract to git. Other repos pull contracts via git.

**Advantages:**
- ✅ Version controlled
- ✅ Works offline (cached)
- ✅ No central server needed
- ✅ Audit trail

**How it works:**
```bash
# Frontend syncs backend contract
specsync bridge sync backend

# Behind the scenes:
# 1. Clone/pull backend repo to temp location
# 2. Copy .kiro/contracts/provided-api.yaml
# 3. Save to frontend/.kiro/contracts/backend-api.yaml
# 4. Compare with previous version
# 5. Show changes
```

### Method 2: HTTP API Sync

Repos expose contracts via HTTP endpoint.

**Configuration:**
```json
{
  "dependencies": {
    "backend": {
      "sync_method": "http",
      "contract_url": "https://api.myapp.com/contracts/backend-api.yaml",
      "auth_token": "${BACKEND_API_TOKEN}"
    }
  }
}
```

### Method 3: Shared Storage Sync

Contracts stored in S3, Azure Blob, etc.

**Configuration:**
```json
{
  "dependencies": {
    "backend": {
      "sync_method": "s3",
      "bucket": "myapp-contracts",
      "key": "backend/provided-api.yaml",
      "region": "us-east-1"
    }
  }
}
```

---

## Contract File Structure

### Provider Contract (What a service provides)

```yaml
# backend/.kiro/contracts/provided-api.yaml
version: "1.0"
repo_id: backend
role: provider
last_updated: "2024-11-27T15:00:00Z"

endpoints:
  - id: get-user
    path: "/users/{id}"
    method: GET
    status: implemented
    implemented_at: "2024-11-20T10:00:00Z"
    
    parameters:
      - name: id
        type: integer
        required: true
    
    response:
      status: 200
      type: object
      schema:
        id: integer
        name: string
        email: string
        avatar_url: string
    
    consumers:
      - frontend
      - mobile

  - id: get-user-posts
    path: "/users/{id}/posts"
    method: GET
    status: implemented
    implemented_at: "2024-11-27T15:00:00Z"
    
    response:
      status: 200
      type: array
      items:
        type: object
        schema:
          id: integer
          title: string
          content: string

models:
  User:
    fields:
      - name: id
        type: integer
      - name: name
        type: string
      - name: email
        type: string
      - name: avatar_url
        type: string
```

### Consumer Contract (What a service expects)

```yaml
# frontend/.kiro/contracts/backend-api.yaml
version: "1.0"
repo_id: frontend
role: consumer
depends_on: backend
last_synced: "2024-11-27T15:30:00Z"

expectations:
  - endpoint: GET /users/{id}
    status: using
    first_used: "2024-11-20T12:00:00Z"
    usage_locations:
      - "src/api/users.ts:15"
      - "src/components/UserProfile.tsx:23"
    
  - endpoint: GET /users/{id}/posts
    status: using
    first_used: "2024-11-27T14:00:00Z"
    usage_locations:
      - "src/api/users.ts:28"
      - "src/components/UserPosts.tsx:10"

# Copy of provider's contract for offline validation
provider_contract:
  endpoints:
    - path: "/users/{id}"
      method: GET
      status: implemented
      response:
        type: object
        schema:
          id: integer
          name: string
          email: string
          avatar_url: string
    
    - path: "/users/{id}/posts"
      method: GET
      status: implemented
      response:
        type: array
        items:
          type: object
```

---

## Commands

```bash
# Initialize bridge in current repo
specsync bridge init --role [provider|consumer]

# Add a dependency
specsync bridge add-dependency backend \
  --git-url https://github.com/myorg/backend.git \
  --contract-path .kiro/contracts/provided-api.yaml

# Sync contracts from dependencies
specsync bridge sync [dependency-name]

# Sync all dependencies
specsync bridge sync --all

# Show what you provide (for providers)
specsync bridge show-contract

# Show what you expect (for consumers)
specsync bridge show-expectations

# Check for drift
specsync bridge validate

# Show dependency graph
specsync bridge graph

# Notify consumers of changes (for providers)
specsync bridge notify-consumers
```

---

## Workflow Examples

### Example 1: Adding Backend as Dependency

```bash
# In frontend repo
cd frontend

# Initialize bridge
specsync bridge init --role consumer

# Add backend dependency
specsync bridge add-dependency backend \
  --git-url https://github.com/myorg/backend.git \
  --contract-path .kiro/contracts/provided-api.yaml

# Sync backend contract
specsync bridge sync backend

# Result:
# ✓ Created .kiro/contracts/backend-api.yaml
# ✓ Found 5 endpoints
# ✓ Ready to validate
```

### Example 2: Multi-Service Setup

```bash
# Backend depends on auth service
cd backend
specsync bridge add-dependency auth-service \
  --git-url https://github.com/myorg/auth-service.git

# Frontend depends on backend AND auth service
cd ../frontend
specsync bridge add-dependency backend \
  --git-url https://github.com/myorg/backend.git
specsync bridge add-dependency auth-service \
  --git-url https://github.com/myorg/auth-service.git

# Mobile depends on backend only
cd ../mobile
specsync bridge add-dependency backend \
  --git-url https://github.com/myorg/backend.git

# Sync all
specsync bridge sync --all
```

---

## Advantages of Decentralized Approach

### 1. **No Shared Folder Required**
- ✅ Repos can be anywhere
- ✅ Different machines
- ✅ Different organizations
- ✅ Different git providers

### 2. **Works Offline**
- ✅ Cached contracts in each repo
- ✅ Validate without network
- ✅ Sync when convenient

### 3. **Flexible Sync Methods**
- ✅ Git (version controlled)
- ✅ HTTP (real-time)
- ✅ S3/Cloud (scalable)
- ✅ Mix and match

### 4. **Gradual Adoption**
- ✅ Add one dependency at a time
- ✅ Not all repos need bridge
- ✅ Works with existing workflows

### 5. **Security**
- ✅ Each repo controls its own contracts
- ✅ No central point of failure
- ✅ Access control via git permissions

---

## Implementation Priority

### Phase 1: MVP (2 repos, git sync)
- [ ] Contract extraction from code
- [ ] Contract storage in `.kiro/contracts/`
- [ ] Git-based sync
- [ ] Basic validation

### Phase 2: Multi-repo (3+ repos)
- [ ] Dependency graph
- [ ] Transitive dependencies
- [ ] Conflict detection

### Phase 3: Advanced Sync
- [ ] HTTP sync method
- [ ] Cloud storage sync
- [ ] Real-time notifications

### Phase 4: Automation
- [ ] Auto-sync on commit
- [ ] Auto-notify consumers
- [ ] GitHub integration

---

## Next Steps

Would you like me to:
1. Create a detailed spec for Phase 1 (MVP)?
2. Implement the contract extraction logic?
3. Build the git-based sync mechanism?
4. Create the CLI commands?

This decentralized approach is much more practical and will work in real-world scenarios where repos are distributed!

# SpecSync

**Keep your specs, code, tests, and docs in perfect sync**

SpecSync is a commit-driven reliability layer that ensures specifications, code, tests, and documentation remain synchronized throughout the development lifecycle. The system acts as a quality gate at commit-time, preventing drift between these critical artifacts before changes enter the codebase.

## Why SpecSync?

Ever committed code only to realize later that:
- Your specs are outdated?
- Tests are missing for new features?
- Documentation doesn't match the implementation?

SpecSync solves this by validating alignment **before** commits are finalized. It's like having a vigilant code reviewer who never sleeps, ensuring your codebase stays consistent and maintainable.

## Features

- ✅ **Automatic validation on commit** - No manual checks needed
- ✅ **Drift detection** - Catches spec-code misalignments instantly
- ✅ **Test coverage validation** - Ensures new code has tests
- ✅ **Documentation sync checking** - Keeps docs current with code
- ✅ **Actionable suggestions** - Tells you exactly what to fix
- ✅ **Customizable steering rules** - Adapts to your project conventions
- ✅ **Fast validation** - Completes in under 30 seconds
- ✅ **Non-invasive** - Preserves your staged changes

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Developer Workflow                       │
│                                                               │
│  git add files → git commit → SpecSync Validation            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Pre-Commit Hook                           │
│  (.kiro/hooks/precommit.json)                               │
│                                                               │
│  Triggers: On commit event                                   │
│  Action: Invoke Kiro agent with validation prompt           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    MCP Git Context Tool                      │
│  (mcp/src/)                                                  │
│                                                               │
│  • Reads: git diff --cached                                  │
│  • Reads: git rev-parse --abbrev-ref HEAD                    │
│  • Returns: Structured git context                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Kiro Agent                              │
│  (Guided by .kiro/steering/rules.md)                        │
│                                                               │
│  1. Parse staged changes                                     │
│  2. Load relevant specs from .kiro/specs/                    │
│  3. Analyze drift:                                           │
│     • Spec ↔ Code alignment                                  │
│     • Code ↔ Test coverage                                   │
│     • Code ↔ Documentation sync                              │
│  4. Generate validation report                               │
│  5. Suggest fixes if drift detected                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Validation Result                         │
│                                                               │
│  ✓ Aligned → Commit proceeds                                 │
│  ✗ Drift detected → Block commit + Show suggestions          │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** (obviously!)
- **Kiro IDE** with MCP support

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/specsync.git
cd specsync
```

### Step 2: Install Python Backend

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix/MacOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Install MCP Tool

```bash
cd mcp
npm install
npm run build
cd ..
```

### Step 4: Configure Kiro MCP Server

Add the SpecSync MCP server to your Kiro configuration:

**Location:** `.kiro/settings/mcp.json` (workspace) or `~/.kiro/settings/mcp.json` (global)

```json
{
  "mcpServers": {
    "specsync-git": {
      "command": "node",
      "args": ["<absolute-path-to-specsync>/mcp/dist/server.js"],
      "disabled": false,
      "autoApprove": ["get_staged_diff"]
    }
  }
}
```

Replace `<absolute-path-to-specsync>` with the full path to your SpecSync installation.

### Step 5: Install Pre-Commit Hook

```bash
python install_hook.py
```

This creates `.git/hooks/pre-commit` that triggers Kiro validation on commits.

### Step 6: Verify Installation

```bash
# Test the MCP tool
cd mcp
node test-manual.js

# Test the backend validation
cd ..
python demo_validation_flow.py

# Run the test suite
pytest
```

## Operating Modes

SpecSync supports three modes for handling drift:

### 1. Blocking Mode (Default)
- ❌ Blocks commits when drift is detected
- ✅ Ensures zero drift in history
- 🎯 Best for: Production code, critical changes

**Configuration:**
```json
{
  "validation": {
    "block_on_drift": true
  },
  "auto_remediation": {
    "enabled": false
  }
}
```

### 2. Task Generation Mode
- ✅ Allows commits to proceed
- ✅ Generates `remediation-tasks.md` with fix instructions
- ✅ Execute tasks one-by-one in Kiro
- 🎯 Best for: Learning, incremental fixes

**Configuration:**
```json
{
  "auto_remediation": {
    "enabled": true,
    "mode": "tasks"
  }
}
```

### 3. Semi-Automatic Mode
- ✅ Allows commits to proceed
- ⚠️ **Requires manual Kiro invocation** after commit
- ✅ Kiro fixes everything in one go
- ✅ Creates follow-up commit automatically
- 🎯 Best for: Rapid development, bulk fixes

**Configuration:**
```json
{
  "auto_remediation": {
    "enabled": true,
    "mode": "semi-auto"
  },
  "semi_auto_fix": {
    "enabled": true
  }
}
```

**Important:** Semi-automatic mode is NOT fully automatic. After each commit, you must:
1. Open Kiro chat
2. Say: "Fix the drift from my last commit"
3. Kiro will then make all fixes and create a commit

See `SPECSYNC_FINAL_REALITY.md` for detailed mode comparison.

## Configuration

### Steering Rules

Customize SpecSync behavior by editing `.kiro/steering/rules.md`:

**File Correlation Patterns** - Define how files relate:
```markdown
backend/handlers/*.py → .kiro/specs/app.yaml
backend/{module}.py → tests/unit/test_{module}.py
```

**Minimal Change Policy** - Control suggestion verbosity:
```markdown
- Suggest only necessary modifications
- Preserve existing structure
- Incremental fixes
```

**Validation Priorities** - Set what matters most:
```markdown
1. Spec Alignment (Highest)
2. Test Coverage (Medium)
3. Documentation (Lower)
```

See `.kiro/steering/rules.md` for complete configuration options.

### Spec Files

Define your service specifications in `.kiro/specs/`:

```yaml
# .kiro/specs/app.yaml
service:
  name: "my-service"
  version: "1.0.0"

endpoints:
  - path: "/users"
    method: "GET"
    description: "List all users"
    response:
      type: "array"
      items: "User"
    tests_required: true

models:
  User:
    fields:
      - name: "id"
        type: "integer"
      - name: "username"
        type: "string"
```

## Usage

### Basic Workflow

1. **Make changes** to your code:
```bash
# Edit backend/handlers/user.py
# Add a new endpoint: GET /users/{id}/posts
```

2. **Stage your changes**:
```bash
git add backend/handlers/user.py
```

3. **Attempt to commit**:
```bash
git commit -m "Add user posts endpoint"
```

4. **SpecSync validates** automatically:
   - Checks if endpoint is in spec
   - Verifies tests exist
   - Confirms documentation is updated

5. **If drift detected**, you'll see:
```
❌ Drift Detected - Commit Blocked

Issues:
1. [SPEC] New endpoint GET /users/{id}/posts not defined in spec
2. [TEST] Missing tests for new endpoint
3. [DOCS] No documentation for new endpoint

Suggestions:
1. Add endpoint definition to .kiro/specs/app.yaml:
   - path: "/users/{id}/posts"
     method: "GET"
     description: "Get posts for a specific user"
     
2. Add tests to tests/unit/test_user.py:
   def test_get_user_posts():
       # Test implementation
       
3. Document endpoint in docs/api/users.md
```

6. **Fix the issues** and commit again:
```bash
# Update spec, tests, and docs
git add .kiro/specs/app.yaml tests/unit/test_user.py docs/api/users.md
git commit -m "Add user posts endpoint with spec, tests, and docs"
```

7. **Commit succeeds** when aligned! ✅

### Demo Scenarios

We've included several demo scripts to showcase SpecSync capabilities:

**Validation Flow Demo:**
```bash
python demo_validation_flow.py
```
Shows the complete validation process with aligned and misaligned changes.

**Drift Detection Demo:**
```bash
python demo_steering_rules.py
```
Demonstrates how steering rules guide validation behavior.

**Performance Monitoring Demo:**
```bash
python demo_performance_monitoring.py
```
Shows validation performance with timing metrics.

**Staging Preservation Demo:**
```bash
python demo_staging_preservation.py
```
Verifies that validation never modifies your staged changes.

**End-to-End Validation Demo:**
```bash
python demo_e2e_validation.py
```
Complete commit flow simulation with the example FastAPI service.

### Example Service

SpecSync includes a working FastAPI service to demonstrate the system:

**Start the service:**
```bash
cd backend
uvicorn main:app --reload
```

**Access the API:**
- Health check: http://localhost:8000/health
- List users: http://localhost:8000/users
- Get user: http://localhost:8000/users/1
- API docs: http://localhost:8000/docs

**Try modifying the service:**
1. Add a new endpoint to `backend/handlers/user.py`
2. Stage and commit the change
3. Watch SpecSync catch the missing spec/tests/docs!

## Project Structure

```
specsync/
├── backend/                    # Python FastAPI backend
│   ├── handlers/               # API endpoint handlers
│   │   ├── health.py           # Health check endpoint
│   │   └── user.py             # User endpoints
│   ├── main.py                 # FastAPI app entry point
│   ├── models.py               # Pydantic data models
│   ├── validator.py            # Main validation orchestrator
│   ├── drift_detector.py       # Spec-code drift detection
│   ├── test_analyzer.py        # Test coverage validation
│   ├── doc_analyzer.py         # Documentation sync checking
│   ├── suggestion_generator.py # Fix suggestion generation
│   ├── steering_parser.py      # Steering rules parser
│   └── rule_application.py     # Rule application logic
├── mcp/                        # Model Context Protocol tool
│   ├── src/
│   │   ├── server.ts           # MCP server implementation
│   │   ├── git.ts              # Git command execution
│   │   └── types.ts            # TypeScript type definitions
│   ├── dist/                   # Compiled JavaScript
│   ├── package.json            # Node.js dependencies
│   └── tsconfig.json           # TypeScript configuration
├── docs/                       # Documentation
│   ├── index.md                # Service overview
│   ├── architecture.md         # System architecture
│   └── api/                    # API documentation
│       ├── health.md           # Health endpoint docs
│       └── users.md            # User endpoints docs
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   │   ├── test_validator.py
│   │   ├── test_drift_detector.py
│   │   ├── test_test_analyzer.py
│   │   └── test_doc_analyzer.py
│   ├── property/               # Property-based tests (Hypothesis)
│   ├── integration/            # Integration tests
│   │   └── test_validation_flow.py
│   └── fixtures/               # Test fixtures and data
├── .kiro/                      # Kiro configuration
│   ├── specs/                  # Feature specifications
│   │   ├── app.yaml            # Example service spec
│   │   └── specsync-core/      # SpecSync system spec
│   │       ├── requirements.md
│   │       ├── design.md
│   │       └── tasks.md
│   ├── steering/               # Steering rules
│   │   └── rules.md            # Validation behavior rules
│   └── hooks/                  # Kiro hooks
│       └── precommit.json      # Pre-commit hook config
├── demo_*.py                   # Demo scripts
├── install_hook.py             # Hook installation script
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
└── README.md                   # This file
```

## Development

### Running Tests

**All tests:**
```bash
pytest
```

**Unit tests only:**
```bash
pytest tests/unit/
```

**Integration tests:**
```bash
pytest tests/integration/
```

**With coverage:**
```bash
pytest --cov=backend --cov-report=html
```

**MCP tool tests:**
```bash
cd mcp
npm test
```

### Running the Example Service

```bash
# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Start the server
cd backend
uvicorn main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

### Code Quality

**Linting:**
```bash
# Python
flake8 backend/ tests/

# TypeScript
cd mcp
npm run lint
```

**Type checking:**
```bash
# Python
mypy backend/

# TypeScript
cd mcp
npm run type-check
```

## Troubleshooting

### Issue: MCP Tool Not Found

**Symptom:** Kiro reports "MCP server 'specsync-git' not found"

**Solution:**
1. Verify MCP tool is built: `cd mcp && npm run build`
2. Check path in `.kiro/settings/mcp.json` is absolute
3. Restart Kiro IDE
4. Check MCP server status in Kiro's MCP panel

### Issue: Pre-Commit Hook Not Triggering

**Symptom:** Commits succeed without validation

**Solution:**
1. Verify hook is installed: `ls -la .git/hooks/pre-commit`
2. Check hook is executable: `chmod +x .git/hooks/pre-commit`
3. Re-run installation: `python install_hook.py`
4. Ensure Kiro is running when committing

### Issue: Validation Takes Too Long

**Symptom:** Validation exceeds 30-second timeout

**Solution:**
1. Check size of staged diff: `git diff --cached --stat`
2. Break large commits into smaller chunks
3. Review steering rules for overly broad patterns
4. Check for performance issues in custom validation logic

### Issue: False Positive Drift Detection

**Symptom:** SpecSync flags valid changes as drift

**Solution:**
1. Review steering rules in `.kiro/steering/rules.md`
2. Add ignore patterns for generated files
3. Update correlation patterns to match your structure
4. Adjust validation priorities if needed

### Issue: Git Commands Fail

**Symptom:** MCP tool returns git errors

**Solution:**
1. Verify you're in a git repository: `git status`
2. Check git is in PATH: `git --version`
3. Ensure repository isn't corrupted: `git fsck`
4. Check file permissions on `.git/` directory

### Issue: Python Import Errors

**Symptom:** `ModuleNotFoundError` when running validation

**Solution:**
1. Activate virtual environment: `source .venv/bin/activate`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (need 3.8+)
4. Verify PYTHONPATH includes project root

### Issue: Node.js Module Errors

**Symptom:** MCP tool fails with module errors

**Solution:**
1. Reinstall dependencies: `cd mcp && npm install`
2. Rebuild TypeScript: `npm run build`
3. Check Node version: `node --version` (need 16+)
4. Clear npm cache: `npm cache clean --force`

### Issue: Steering Rules Not Applied

**Symptom:** Rule changes don't take effect

**Solution:**
1. Verify syntax in `.kiro/steering/rules.md`
2. Check for YAML/Markdown formatting errors
3. Rules reload automatically - no restart needed
4. Test with a fresh commit to trigger validation

### Issue: Specs Not Found

**Symptom:** Validation reports "spec file not found"

**Solution:**
1. Verify spec exists: `ls .kiro/specs/app.yaml`
2. Check file path in steering rules
3. Ensure spec file is valid YAML
4. Review correlation patterns in steering rules

### Getting Help

If you encounter issues not covered here:

1. **Check the logs:** Look for error messages in Kiro's output panel
2. **Run demos:** Execute demo scripts to verify system functionality
3. **Review specs:** Check `.kiro/specs/specsync-core/` for detailed design
4. **Test components:** Run unit tests to isolate the problem
5. **Open an issue:** Report bugs on GitHub with reproduction steps

## Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest && cd mcp && npm test`
5. Commit with SpecSync validation: `git commit -m "Add amazing feature"`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Open a Pull Request

Please ensure:
- All tests pass
- Code follows existing style
- Specs are updated for new features
- Documentation is current

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built with:
- [Kiro IDE](https://kiro.ai) - AI-powered development environment
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Hypothesis](https://hypothesis.readthedocs.io/) - Property-based testing
- [Model Context Protocol](https://modelcontextprotocol.io/) - LLM integration standard

---

**SpecSync** - Because drift is a bug waiting to happen. Catch it before commit.

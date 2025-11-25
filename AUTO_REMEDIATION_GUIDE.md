# SpecSync Auto-Remediation Mode

## Overview

Auto-remediation mode allows SpecSync to **automatically generate tasks** to fix detected drift instead of blocking your commits. This gives you flexibility to commit code and fix alignment issues on your own schedule.

---

## 🎯 Two Modes of Operation

### Mode 1: Blocking Mode (Default)
- ❌ Commit blocked when drift detected
- 💡 Suggestions provided
- ✋ Must fix before committing

**Best for:** Production releases, critical changes

### Mode 2: Auto-Remediation Mode (New!)
- ✅ Commit allowed even with drift
- 📋 Tasks file automatically generated
- 🔧 Fix drift at your own pace

**Best for:** Development, prototyping, large changes

---

## 🚀 How to Enable

### Option 1: Configuration File (Persistent)

Create or edit `.kiro/settings/specsync.json`:

```json
{
  "auto_remediation": {
    "enabled": true,
    "mode": "tasks",
    "description": "Generate tasks instead of blocking commits"
  },
  "validation": {
    "block_on_drift": false,
    "allow_commit_with_tasks": true
  },
  "task_generation": {
    "create_in_spec_folder": true,
    "file_name": "remediation-tasks.md",
    "include_priority": true,
    "include_timestamps": true
  }
}
```

### Option 2: Ask Kiro (One-time)

In Kiro chat:
```
"Enable auto-remediation mode for SpecSync"
```

or

```
"Validate my changes and generate remediation tasks"
```

---

## 📋 What Gets Generated

When drift is detected, SpecSync creates:

**File:** `.kiro/specs/app/remediation-tasks.md`

**Contents:**
```markdown
# Remediation Tasks

**Generated:** 2025-11-25 22:00:00
**Feature:** app
**Total Tasks:** 5

## Tasks by Priority

### 📋 Specification Updates

- [ ] **Add missing endpoint to spec**
  - **File:** `.kiro/specs/app.yaml`
  - **Priority:** 9/10
  - **Details:** Add definition for GET /users/{id}/posts
  - **Created:** 2025-11-25T22:00:00

### 🧪 Test Coverage

- [ ] **Create tests for backend/handlers/user.py**
  - **File:** `tests/unit/test_user.py`
  - **Priority:** 7/10
  - **Details:** Add unit tests covering all functions
  - **Created:** 2025-11-25T22:00:00

### 📚 Documentation

- [ ] **Document new API endpoint**
  - **File:** `docs/api/users.md`
  - **Priority:** 5/10
  - **Details:** Document GET /users/{id}/posts endpoint
  - **Created:** 2025-11-25T22:00:00
```

---

## 🔄 Workflow Example

### Step 1: Make Changes
```bash
# Add new endpoint to code
vim backend/handlers/user.py
```

### Step 2: Commit (Auto-Remediation Enabled)
```bash
git add backend/handlers/user.py
git commit -m "Add user posts endpoint"
```

### Step 3: SpecSync Validates
```
🔍 Running SpecSync validation...
🔧 Auto-remediation mode: ENABLED

❌ FAILURE: Validation issues detected
   - Missing spec definition
   - No tests
   - Missing documentation

🔧 Auto-Remediation Tasks Generated!
📁 Tasks file: .kiro/specs/app/remediation-tasks.md
📊 Total tasks: 3

✅ Commit ALLOWED with remediation tasks generated
```

### Step 4: Review Tasks
```bash
cat .kiro/specs/app/remediation-tasks.md
```

### Step 5: Complete Tasks
```bash
# Fix spec
vim .kiro/specs/app.yaml

# Add tests
vim tests/unit/test_user.py

# Update docs
vim docs/api/users.md

# Check off tasks in remediation-tasks.md
```

### Step 6: Commit Fixes
```bash
git add .kiro/specs/app.yaml tests/ docs/
git commit -m "Complete remediation tasks for user posts endpoint"
```

### Step 7: Validation Passes
```
✅ SUCCESS: All validations passed
```

---

## ⚙️ Configuration Options

### `auto_remediation.enabled`
- **Type:** boolean
- **Default:** `false`
- **Description:** Enable/disable auto-remediation mode

### `auto_remediation.mode`
- **Type:** string
- **Options:** `"tasks"`, `"auto-fix"` (future)
- **Default:** `"tasks"`
- **Description:** How to handle remediation

### `validation.block_on_drift`
- **Type:** boolean
- **Default:** `true`
- **Description:** Block commits when drift detected (ignored if auto-remediation enabled)

### `validation.allow_commit_with_tasks`
- **Type:** boolean
- **Default:** `true`
- **Description:** Allow commits when tasks are generated

### `task_generation.create_in_spec_folder`
- **Type:** boolean
- **Default:** `true`
- **Description:** Create tasks file in spec folder

### `task_generation.file_name`
- **Type:** string
- **Default:** `"remediation-tasks.md"`
- **Description:** Name of generated tasks file

### `task_generation.include_priority`
- **Type:** boolean
- **Default:** `true`
- **Description:** Include priority levels in tasks

### `task_generation.include_timestamps`
- **Type:** boolean
- **Default:** `true`
- **Description:** Include creation timestamps

---

## 🎨 Task Priority Levels

Tasks are prioritized from 1-10:

| Priority | Level | Description |
|----------|-------|-------------|
| 9-10 | Critical | Spec alignment issues |
| 7-8 | High | Test coverage gaps |
| 5-6 | Medium | Documentation updates |
| 3-4 | Low | Code quality improvements |
| 1-2 | Optional | Nice-to-have fixes |

---

## 💡 Best Practices

### ✅ DO:
- Enable auto-remediation during active development
- Review generated tasks before starting work
- Complete high-priority tasks first
- Commit fixes together when possible
- Re-run validation after completing tasks

### ❌ DON'T:
- Leave tasks incomplete for too long
- Ignore critical (9-10) priority tasks
- Commit to production with open tasks
- Delete tasks file without fixing issues
- Enable for production releases

---

## 🔧 Troubleshooting

### Tasks Not Generated

**Problem:** Commits blocked even with auto-remediation enabled

**Solution:**
1. Check `.kiro/settings/specsync.json` exists
2. Verify `"enabled": true`
3. Ensure `"allow_commit_with_tasks": true`
4. Restart Kiro IDE

### Tasks File Not Found

**Problem:** Can't find generated tasks file

**Solution:**
```bash
# Check default location
ls .kiro/specs/app/remediation-tasks.md

# Search for it
find .kiro -name "remediation-tasks.md"
```

### Want to Disable

**Problem:** Want to go back to blocking mode

**Solution:**
Edit `.kiro/settings/specsync.json`:
```json
{
  "auto_remediation": {
    "enabled": false
  }
}
```

Or delete the config file to use defaults.

---

## 🚀 Advanced Usage

### Custom Task Templates

You can customize task generation by editing `backend/auto_remediation.py`:

```python
# Customize task descriptions
task = RemediationTask(
    task_type='spec',
    description='Your custom description',
    file='path/to/file',
    details='Detailed instructions',
    priority=8
)
```

### Integration with Task Trackers

Export tasks to your project management tool:

```bash
# Convert to JSON
python -c "
import json
from backend.auto_remediation import AutoRemediationEngine
engine = AutoRemediationEngine('app')
# ... generate tasks ...
print(json.dumps([t.to_dict() for t in tasks], indent=2))
"
```

### Batch Processing

Process multiple features:

```bash
# Generate tasks for all features
for feature in .kiro/specs/*/; do
    python run_validation.py --feature $(basename $feature)
done
```

---

## 📊 Example Scenarios

### Scenario 1: Rapid Prototyping

**Situation:** Building a prototype, need to move fast

**Solution:**
```json
{
  "auto_remediation": {"enabled": true},
  "validation": {"allow_commit_with_tasks": true}
}
```

**Result:** Commit freely, fix drift later

### Scenario 2: Team Development

**Situation:** Multiple developers, want to track drift fixes

**Solution:**
- Enable auto-remediation
- Commit tasks file to git
- Assign tasks to team members
- Track completion in tasks file

### Scenario 3: Pre-Release Cleanup

**Situation:** Before release, need to fix all drift

**Solution:**
```bash
# Disable auto-remediation
# Complete all open tasks
# Re-enable blocking mode for release
```

---

## 🎯 Summary

Auto-remediation mode gives you **flexibility** without sacrificing **quality**:

- ✅ Commit when you need to
- 📋 Track what needs fixing
- 🎯 Prioritize your work
- 🔧 Fix drift on your schedule
- ✨ Maintain code quality

**Enable it today and experience drift-free development with flexibility!**

---

## 📚 Related Documentation

- [SpecSync Setup Guide](KIRO_SETUP_COMPLETE.md)
- [Testing Guide](TEST_SCENARIOS.md)
- [Steering Rules](.kiro/steering/rules.md)
- [Configuration Reference](.kiro/settings/specsync.json)

---

**Questions?** Ask Kiro: "How do I use auto-remediation mode?"

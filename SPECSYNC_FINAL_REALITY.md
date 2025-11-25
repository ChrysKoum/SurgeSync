# SpecSync User Guide

## Understanding SpecSync Modes

SpecSync provides three operating modes for handling drift between specs, code, tests, and documentation:

## ✅ What DOES Work

### 1. Automatic Drift Detection
- ✅ Runs on every commit
- ✅ Detects spec-code-test-doc misalignment
- ✅ Fast (completes in <1 second)
- ✅ Comprehensive reporting

### 2. Three Operating Modes

#### Mode 1: Blocking (Traditional)
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

**Behavior:**
- ❌ Blocks commit if drift detected
- ✅ Forces you to fix before committing
- ✅ No drift ever enters history

**Use when:** Working on production code, want zero drift

#### Mode 2: Task Generation (Recommended)
```json
{
  "auto_remediation": {
    "enabled": true,
    "mode": "tasks"
  }
}
```

**Behavior:**
- ✅ Allows commit to proceed
- ✅ Generates `remediation-tasks.md` file
- ✅ Tasks can be executed one-by-one in Kiro
- ✅ Full control over what gets fixed

**Use when:** Rapid development, want to fix later

#### Mode 3: Semi-Automatic Fix
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

**Behavior:**
- ✅ Allows commit to proceed
- ✅ Shows message: "Ask Kiro to fix the drift"
- ⚠️ **You manually open Kiro and ask** (required step)
- ✅ Kiro fixes everything in one go
- ✅ Kiro creates follow-up commit

**Use when:** Want bulk fixes, comfortable with AI-generated code

**Important:** This mode is NOT fully automatic. You must manually invoke Kiro after each commit.

## ❌ What Is NOT Supported

### Fully Automatic Background Processing

**Not possible:**
```
git commit → Drift detected → Kiro automatically opens → 
Kiro automatically fixes → Kiro automatically commits
```

**Why:**
- No API to programmatically start Kiro agent sessions
- No background processing capability in Kiro IDE
- Requires manual user invocation

**What actually works (semi-automatic):**
```
git commit → Drift detected → Commit proceeds → 
Message shown → YOU open Kiro → YOU ask Kiro to fix → 
Kiro fixes → Kiro commits
```

The manual step of asking Kiro is required and cannot be automated.

## 🎯 Recommended Workflow

### For Rapid Development (Task Mode)

```bash
# 1. Configure task mode
# Edit .kiro/settings/specsync.json:
{
  "auto_remediation": {
    "enabled": true,
    "mode": "tasks"
  }
}

# 2. Make changes and commit
git add .
git commit -m "Add user posts endpoint"

# 3. SpecSync generates tasks
# Opens: .kiro/specs/app/remediation-tasks.md

# 4. Execute tasks in Kiro
# Click "Start task" on each item
# Kiro executes them one by one

# 5. Commit fixes
git add .
git commit -m "Fix drift from previous commit"
```

### For Bulk Fixes (Semi-Automatic Mode)

```bash
# 1. Configure semi-auto mode
# Edit .kiro/settings/specsync.json:
{
  "auto_remediation": {
    "enabled": true,
    "mode": "semi-auto"
  },
  "semi_auto_fix": {
    "enabled": true
  }
}

# 2. Make changes and commit
git add .
git commit -m "Add user posts endpoint"

# 3. SpecSync allows commit and shows message
✅ Commit ALLOWED - Manual Kiro invocation required
💡 After commit, open Kiro and say: 'Fix the drift from my last commit'

# 4. MANUALLY open Kiro chat and say:
"Fix the drift from my last commit"

# 5. Kiro does everything:
# - Updates specs
# - Creates tests
# - Writes docs
# - Creates commit

# 6. Result: Clean two-commit history
abc123 - Add user posts endpoint
def456 - 🤖 SpecSync: Auto-fix drift
```

**Note:** Step 4 (manually invoking Kiro) is required and cannot be skipped.

### For Production (Blocking Mode)

```bash
# 1. Configure blocking mode
# Edit .kiro/settings/specsync.json:
{
  "validation": {
    "block_on_drift": true
  },
  "auto_remediation": {
    "enabled": false
  }
}

# 2. Make changes and try to commit
git add .
git commit -m "Add user posts endpoint"

# 3. SpecSync blocks commit
❌ Commit BLOCKED - Fix drift before committing

# 4. Fix issues manually or with Kiro

# 5. Commit again
git commit -m "Add user posts endpoint"

# 6. Result: Single clean commit with no drift
abc123 - Add user posts endpoint (fully aligned)
```

## 📊 Mode Comparison

| Feature | Blocking | Tasks | Semi-Auto |
|---------|----------|-------|-----------|
| Commit proceeds | ❌ No | ✅ Yes | ✅ Yes |
| Drift in history | ❌ Never | ⚠️ Briefly | ⚠️ Briefly |
| Manual work | 🔴 High | 🟡 Medium | 🟡 Medium* |
| Control | 🟢 Full | 🟢 Full | 🟡 Medium |
| Speed | 🔴 Slow | 🟡 Medium | 🟢 Fast |
| Kiro invocation | Manual | Per-task | **Manual (required)** |
| Best for | Production | Learning | Rapid dev |

*Semi-auto requires manual Kiro invocation after each commit

## 💡 Key Insights

### What Makes SpecSync Valuable

Even without fully automatic background processing, SpecSync provides:

1. **Instant Drift Detection** - Know immediately when things are out of sync
2. **Comprehensive Analysis** - Checks specs, tests, AND docs
3. **Actionable Suggestions** - Tells you exactly what to fix
4. **Flexible Modes** - Choose your workflow
5. **Kiro Integration** - AI-powered fixes when you want them

### The Manual Step is Actually Good

Having to manually invoke Kiro for fixes is a **feature, not a bug**:

- ✅ You review what needs fixing
- ✅ You control when fixes happen
- ✅ You can adjust the approach
- ✅ No surprise commits
- ✅ No unexpected credit usage

### Future Possibilities

For truly automatic background processing, we would need:

1. **Kiro IDE Plugin API** - Official extension system
2. **Background Agent API** - Programmatic agent control
3. **Credit Pre-Authorization** - Automatic credit approval
4. **Hook System Enhancement** - Reliable automatic triggers

These would require changes to Kiro IDE itself, not just SpecSync.

## 🚀 Getting Started

### Quick Setup

1. **Install the git hook:**
   ```bash
   python install_hook.py
   ```

2. **Choose your mode:**
   - Edit `.kiro/settings/specsync.json`
   - Set `mode` to `"tasks"` or `"auto-fix"`

3. **Make a commit:**
   ```bash
   git commit -m "Your changes"
   ```

4. **Follow the prompts:**
   - Task mode: Execute tasks in Kiro
   - Auto-fix mode: Ask Kiro to fix drift

### Example Session

```bash
$ git commit -m "Add user posts endpoint"

🤖 Auto-fix mode: ENABLED

❌ Drift detected:
   - Missing spec definition
   - No tests
   - Missing documentation

✅ Commit ALLOWED - Ask Kiro to fix the drift

[main abc123] Add user posts endpoint
 1 file changed, 10 insertions(+)

$ # Now open Kiro and say:
$ # "Fix the drift from my last commit"

# Kiro responds and creates:
[main def456] 🤖 SpecSync: Auto-fix drift
 3 files changed, 150 insertions(+)

$ git log --oneline
def456 🤖 SpecSync: Auto-fix drift
abc123 Add user posts endpoint
```

## 📝 Summary

**SpecSync is a powerful drift detection and remediation system** that:

- ✅ Detects drift automatically on every commit
- ✅ Provides three flexible operating modes
- ✅ Integrates with Kiro for AI-powered fixes
- ✅ Maintains clean git history
- ⚠️ Requires manual Kiro invocation for fixes

**It's not fully automatic**, but it's the best we can achieve with current Kiro capabilities, and the manual step actually provides valuable control and transparency.

**Use it to maintain spec-code-test-doc alignment** without the pain of manual tracking and fixing.

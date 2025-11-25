# 🤖 SpecSync Auto-Fix Mode - Complete Guide

## Overview

Auto-fix mode is the **ultimate automation** for SpecSync. Instead of just detecting drift or generating tasks, Kiro automatically fixes everything and creates a clean commit.

---

## 🎯 Three Modes Comparison

| Feature | Blocking Mode | Task Mode | Auto-Fix Mode |
|---------|--------------|-----------|---------------|
| Commit behavior | ❌ Blocked | ✅ Allowed | ✅ Allowed |
| Drift detection | ✅ Yes | ✅ Yes | ✅ Yes |
| Task generation | ❌ No | ✅ Yes | ✅ Yes |
| Automatic fixes | ❌ No | ❌ No | ✅ Yes |
| Kiro agent | ❌ Not needed | ❌ Not needed | ✅ Required |
| User credits | ❌ Not needed | ❌ Not needed | ✅ Required |
| Git commits | 1 (manual) | 1 (manual) | 2 (automatic) |

---

## 🚀 How Auto-Fix Works

### Step-by-Step Process

1. **You commit code** (with drift)
   ```bash
   git commit -m "Add user posts endpoint"
   ```

2. **SpecSync validates** (detects drift)
   - Missing spec definition
   - No tests
   - Missing documentation

3. **Kiro agent activates** (auto-fix mode)
   - Updates `.kiro/specs/app.yaml`
   - Creates `tests/unit/test_user.py`
   - Writes `docs/api/users.md`

4. **Kiro commits fixes** (separate commit)
   ```bash
   🤖 SpecSync: Auto-fix drift for "Add user posts endpoint"
   ```

5. **Clean git history**
   ```
   abc123 - Add user posts endpoint
   def456 - 🤖 SpecSync: Auto-fix drift for "Add user posts endpoint"
   ```

---

## ⚙️ Configuration

### Enable Auto-Fix Mode

Edit `.kiro/settings/specsync.json`:

```json
{
  "auto_remediation": {
    "enabled": true,
    "mode": "auto-fix"
  },
  "auto_fix": {
    "enabled": true,
    "require_user_credits": true,
    "create_separate_commit": true,
    "commit_message_template": "🤖 SpecSync: Auto-fix drift for {original_commit}",
    "amend_original_commit": false
  }
}
```



### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `auto_remediation.mode` | string | `"tasks"` | Set to `"auto-fix"` for full automation |
| `auto_fix.enabled` | boolean | `false` | Enable/disable auto-fix |
| `auto_fix.require_user_credits` | boolean | `true` | Require credits for auto-fix |
| `auto_fix.create_separate_commit` | boolean | `true` | Create separate commit vs amend |
| `auto_fix.amend_original_commit` | boolean | `false` | Amend original instead of separate |
| `git.auto_push` | boolean | `false` | Auto-push after fix commit |

---

## 💰 Credits & Cost

### Credit Usage

Auto-fix uses Kiro credits based on complexity:

- **Spec updates:** ~1 credit per endpoint/function
- **Test generation:** ~2 credits per test file
- **Documentation:** ~1 credit per doc section
- **Minimum:** 3 credits per auto-fix

### Example Costs

| Scenario | Estimated Credits |
|----------|------------------|
| 1 new endpoint | 3-5 credits |
| 3 new endpoints | 8-12 credits |
| New module with 5 functions | 15-20 credits |
| Large refactor | 25-40 credits |

### Credit Check

Before auto-fix runs, Kiro will:
1. Estimate credits needed
2. Check your balance
3. Ask for confirmation (if configured)
4. Proceed with fixes

---

## 🔄 Git History Options

### Option 1: Separate Commit (Recommended)

**Configuration:**
```json
{
  "auto_fix": {
    "create_separate_commit": true,
    "amend_original_commit": false
  }
}
```

**Result:**
```
commit abc123
Author: You
Date: Today
    Add user posts endpoint

commit def456
Author: Kiro Bot
Date: Today
    🤖 SpecSync: Auto-fix drift for "Add user posts endpoint"
    
    - Updated .kiro/specs/app.yaml
    - Created tests/unit/test_user.py
    - Added docs/api/users.md
```

**Benefits:**
- ✅ Clear history of what was automated
- ✅ Easy to review Kiro's changes
- ✅ Can revert auto-fixes separately
- ✅ Transparent process

### Option 2: Amend Original

**Configuration:**
```json
{
  "auto_fix": {
    "create_separate_commit": false,
    "amend_original_commit": true
  }
}
```

**Result:**
```
commit abc123
Author: You
Date: Today
    Add user posts endpoint
    
    Files changed:
    - backend/handlers/user.py
    - .kiro/specs/app.yaml (auto-fixed)
    - tests/unit/test_user.py (auto-fixed)
    - docs/api/users.md (auto-fixed)
```

**Benefits:**
- ✅ Single commit
- ✅ Cleaner history
- ⚠️ Less transparent
- ⚠️ Can't separate manual vs auto changes

---

## 🛡️ Safety & Control

### User Confirmation

Configure confirmation prompts:

```json
{
  "auto_fix": {
    "require_confirmation": true,
    "show_preview": true,
    "allow_edit_before_commit": true
  }
}
```

### Review Before Commit

Kiro can show you changes before committing:

```
🤖 Auto-Fix Preview

Files to be modified:
  M .kiro/specs/app.yaml
  A tests/unit/test_user.py
  M docs/api/users.md

Changes:
  + Added endpoint definition for GET /users/{id}/posts
  + Created 3 unit tests
  + Documented new endpoint

Proceed with commit? [Y/n]
```

### Rollback

If you don't like the auto-fixes:

```bash
# Revert the auto-fix commit
git revert HEAD

# Or reset to before auto-fix
git reset --hard HEAD~1
```

---

## 📋 What Gets Auto-Fixed

### Specifications

Kiro will add to `.kiro/specs/app.yaml`:

```yaml
- path: "/users/{id}/posts"
  method: "GET"
  description: "Get posts for a specific user"
  parameters:
    - name: "id"
      type: "integer"
  response:
    type: "object"
  tests_required: true
```

### Tests

Kiro will create `tests/unit/test_user.py`:

```python
def test_get_user_posts():
    """Test getting posts for a user."""
    response = client.get("/users/1/posts")
    assert response.status_code == 200
    assert "posts" in response.json()
```

### Documentation

Kiro will update `docs/api/users.md`:

```markdown
### GET /users/{id}/posts

Get all posts for a specific user.

**Parameters:**
- `id` (integer): User ID

**Response:**
```json
{
  "user_id": 1,
  "posts": []
}
```
```

---

## 🎮 Usage Examples

### Example 1: Simple Endpoint Addition

**Your commit:**
```bash
# Add endpoint to code
vim backend/handlers/user.py

git add backend/handlers/user.py
git commit -m "Add user posts endpoint"
```

**Kiro auto-fixes:**
```
🤖 Auto-fix mode: ENABLED

❌ Drift detected:
   - Missing spec definition
   - No tests
   - Missing documentation

🤖 Kiro Agent Auto-Fix
   Estimated credits: 4

📋 Kiro will automatically:
   ✓ Update specifications
   ✓ Create tests
   ✓ Add documentation

✅ Commit ALLOWED - Kiro will auto-fix drift in background

[2 seconds later]

✅ Auto-fix complete!
   Created commit: 🤖 SpecSync: Auto-fix drift for "Add user posts endpoint"
```

### Example 2: Multiple Endpoints

**Your commit:**
```bash
# Add 3 new endpoints
git commit -m "Add posts, comments, and likes endpoints"
```

**Kiro auto-fixes:**
```
Estimated credits: 12

Kiro will fix:
  - 3 spec definitions
  - 3 test files
  - 3 documentation sections

Proceed? [Y/n] y

✅ Auto-fix complete! (used 11 credits)
```

### Example 3: With Confirmation

**Configuration:**
```json
{
  "auto_fix": {
    "require_confirmation": true
  }
}
```

**Process:**
```
🤖 Auto-Fix Preview

Estimated credits: 5

Changes to be made:
  1. Update .kiro/specs/app.yaml
     + Add GET /users/{id}/posts endpoint
  
  2. Create tests/unit/test_user.py
     + test_get_user_posts()
     + test_get_user_posts_empty()
  
  3. Update docs/api/users.md
     + Document GET /users/{id}/posts

Proceed with auto-fix? [Y/n/preview]
```

---

## 🔧 Advanced Configuration

### Custom Commit Messages

```json
{
  "auto_fix": {
    "commit_message_template": "🔧 Auto-fix: {original_commit}\n\nFixed by SpecSync:\n{fixes_summary}"
  }
}
```

### Selective Auto-Fix

Only auto-fix certain types:

```json
{
  "auto_fix": {
    "fix_specs": true,
    "fix_tests": true,
    "fix_docs": false
  }
}
```

### Credit Limits

Set maximum credits per auto-fix:

```json
{
  "auto_fix": {
    "max_credits_per_fix": 20,
    "warn_above_credits": 10
  }
}
```

---

## 🚨 Troubleshooting

### Auto-Fix Not Working

**Problem:** Commits proceed but no auto-fix happens

**Solutions:**
1. Check configuration: `cat .kiro/settings/specsync.json`
2. Verify mode is `"auto-fix"`
3. Ensure `auto_fix.enabled: true`
4. Check Kiro agent is running
5. Verify you have credits

### Insufficient Credits

**Problem:** "Not enough credits for auto-fix"

**Solutions:**
1. Check credit balance in Kiro
2. Reduce scope of changes
3. Switch to task mode temporarily
4. Purchase more credits

### Auto-Fix Creates Wrong Code

**Problem:** Generated tests/docs are incorrect

**Solutions:**
1. Review and edit the auto-fix commit
2. Provide more context in commit message
3. Update steering rules for better guidance
4. Use task mode for complex changes

---

## 💡 Best Practices

### ✅ DO:

- Use auto-fix for routine endpoint additions
- Review auto-fix commits before pushing
- Keep commit messages descriptive
- Set credit limits to avoid surprises
- Use confirmation mode for large changes

### ❌ DON'T:

- Use auto-fix for complex refactoring
- Blindly trust all auto-generated code
- Use on production branches without review
- Disable safety checks
- Ignore credit costs

---

## 🎯 When to Use Each Mode

### Use Blocking Mode When:
- Working on production releases
- Making critical changes
- Want full control
- No time pressure

### Use Task Mode When:
- Prototyping quickly
- Want to review before fixing
- Working with team
- Learning the codebase

### Use Auto-Fix Mode When:
- Adding routine endpoints
- Have credits available
- Trust Kiro's judgment
- Want maximum speed
- Maintaining clean history

---

## 📊 Comparison Summary

| Aspect | Blocking | Tasks | Auto-Fix |
|--------|----------|-------|----------|
| Speed | ⭐ Slow | ⭐⭐ Medium | ⭐⭐⭐ Fast |
| Control | ⭐⭐⭐ Full | ⭐⭐ High | ⭐ Medium |
| Automation | ⭐ None | ⭐⭐ Partial | ⭐⭐⭐ Full |
| Cost | Free | Free | Credits |
| Best for | Production | Development | Rapid dev |

---

## 🚀 Getting Started

### Quick Start

1. **Enable auto-fix:**
   ```bash
   # Edit .kiro/settings/specsync.json
   # Set mode to "auto-fix"
   ```

2. **Make a change:**
   ```bash
   # Add new endpoint
   vim backend/handlers/user.py
   ```

3. **Commit:**
   ```bash
   git commit -m "Add user posts endpoint"
   ```

4. **Watch Kiro work:**
   ```
   🤖 Auto-fixing drift...
   ✅ Done! Check the follow-up commit.
   ```

---

**Experience the future of drift-free development!** 🚀

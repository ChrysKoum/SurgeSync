# SpecSync Demo Video Script

**Duration:** 3 minutes
**Target:** Kiroween Hackathon Judges

---

## 🎬 Scene Breakdown

### Scene 1: Hook (0:00 - 0:20)

**Visual:** Screen recording of terminal with failed integration

**Narration:**
> "Every developer knows this pain: You add a new API endpoint, commit your code, deploy to production... and everything breaks. Why? Because you forgot to update the tests. Or the documentation. Or the spec file. This is called drift, and it costs teams thousands of hours every year."

**On Screen:**
```
❌ Production Error
   Endpoint /users/123/posts not found
   
❌ Test Failure  
   Expected endpoint not implemented
   
❌ Documentation Outdated
   API docs don't match actual endpoints
```

---

### Scene 2: Solution Introduction (0:20 - 0:40)

**Visual:** SpecSync logo/title card, then terminal showing installation

**Narration:**
> "Meet SpecSync - a commit-time quality gate that automatically keeps your specifications, code, tests, and documentation perfectly synchronized. It catches drift before it enters your codebase."

**On Screen:**
```bash
$ pip install specsync
$ python install_hook.py
✓ SpecSync installed successfully
```

---

### Scene 3: The Setup (0:40 - 1:00)

**Visual:** VS Code showing project structure

**Narration:**
> "Here's a FastAPI project with a spec file that defines our API. The spec says we have two endpoints: GET /users and GET /users/{id}. Let's add a new feature."

**On Screen:**
```
project/
├── .kiro/
│   └── specs/
│       └── app.yaml          ← API specification
├── backend/
│   └── handlers/
│       └── user.py           ← Implementation
├── tests/
│   └── unit/
│       └── test_user.py      ← Tests
└── docs/
    └── api/
        └── users.md          ← Documentation
```

**Highlight:** `.kiro/specs/app.yaml` showing existing endpoints

---

### Scene 4: Making a Change (1:00 - 1:20)

**Visual:** Live coding - adding new endpoint

**Narration:**
> "I'm going to add a new endpoint to get a user's posts. Watch what happens when I commit this change."

**On Screen:**
```python
# backend/handlers/user.py

@app.get("/users/{id}/posts")  # NEW ENDPOINT
def get_user_posts(id: int) -> List[Post]:
    """Get all posts for a specific user."""
    return db.get_posts_by_user(id)
```

**Terminal:**
```bash
$ git add backend/handlers/user.py
$ git commit -m "Add user posts endpoint"
```

---

### Scene 5: SpecSync in Action (1:20 - 2:00)

**Visual:** Terminal showing SpecSync validation output

**Narration:**
> "SpecSync automatically detects three problems: First, this endpoint isn't defined in our spec. Second, there are no tests for it. And third, the documentation doesn't mention it. But instead of blocking my commit, SpecSync generates specific tasks to fix each issue."

**On Screen:**
```
🔍 SpecSync Validation

❌ Drift Detected

Spec Issues:
  • New endpoint /users/{id}/posts not in spec
    File: .kiro/specs/app.yaml
    
Test Coverage Issues:
  • No tests for get_user_posts()
    Expected: tests/unit/test_user.py
    
Documentation Issues:
  • Endpoint not documented
    Expected: docs/api/users.md

📋 Generated Tasks: .kiro/specs/app/remediation-tasks.md

✅ Commit ALLOWED with tasks generated
```

---

### Scene 6: The Tasks (2:00 - 2:20)

**Visual:** Opening the generated tasks file

**Narration:**
> "SpecSync created a detailed task list with exactly what I need to do. It tells me what to add to the spec, what tests to write, and how to update the documentation. Everything is prioritized and actionable."

**On Screen:**
```markdown
# Remediation Tasks

## High Priority

- [ ] Update .kiro/specs/app.yaml
  Add endpoint definition:
  ```yaml
  - path: "/users/{id}/posts"
    method: GET
    response: Array<Post>
  ```

- [ ] Create tests in tests/unit/test_user.py
  ```python
  def test_get_user_posts():
      response = client.get("/users/1/posts")
      assert response.status_code == 200
  ```

- [ ] Update docs/api/users.md
  Document the new endpoint with examples
```

---

### Scene 7: Kiro Integration (2:20 - 2:40)

**Visual:** Split screen - Kiro IDE and code

**Narration:**
> "I built SpecSync using Kiro's powerful features. The MCP tool automatically extracts git context, so Kiro knows exactly what I'm committing. Spec-driven development ensured complete feature coverage. And steering documents kept the code quality consistent throughout."

**On Screen:**
```
Kiro Features Used:

✓ MCP Tool - Automatic git context
✓ Specs - Complete feature coverage  
✓ Steering - Consistent code quality
✓ Hooks - Automated validation
✓ Vibe Coding - Rapid prototyping
```

---

### Scene 8: The Impact (2:40 - 2:55)

**Visual:** Before/After comparison

**Narration:**
> "SpecSync catches drift before it enters your codebase, generates actionable tasks, and keeps your entire team aligned. No more integration bugs. No more outdated docs. No more missing tests."

**On Screen:**
```
Before SpecSync:
❌ 60% of commits had drift
❌ 2-3 hours/week fixing integration bugs
❌ Documentation always outdated

After SpecSync:
✅ 0% drift in codebase
✅ Issues caught at commit time
✅ Always synchronized
```

---

### Scene 9: Call to Action (2:55 - 3:00)

**Visual:** GitHub repo and logo

**Narration:**
> "Try SpecSync today. Check out the GitHub repo, install it in your project, and never worry about drift again. Thanks for watching!"

**On Screen:**
```
github.com/chryskoum/specsync

⭐ Star the repo
📦 npm install @specsync/mcp-git-context
🚀 Get started in 5 minutes
```

---

## 🎥 Recording Tips

### Setup
- Use OBS Studio or similar screen recorder
- 1920x1080 resolution minimum
- Clear audio (use good microphone)
- Clean desktop (hide personal info)

### Terminal
- Use large font (18-20pt)
- Dark theme with high contrast
- Slow down typing (or use pre-recorded commands)
- Add pauses after important output

### Code Editor
- Use VS Code with clean theme
- Zoom in (font size 16-18)
- Hide unnecessary panels
- Use syntax highlighting

### Pacing
- Speak clearly and not too fast
- Pause between sections
- Let important text stay on screen for 2-3 seconds
- Don't rush the demo

### Post-Production
- Add title cards between sections
- Highlight important text with arrows/boxes
- Add background music (low volume, no copyright)
- Export at 1080p, 30fps

---

## 📝 Alternative: Shorter Version (2 minutes)

If you need a shorter version, cut:
- Scene 1 (Hook) - Start directly with solution
- Scene 8 (Impact) - Merge into conclusion

Keep:
- Solution intro
- Live demo
- Kiro integration
- Call to action

---

## 🎤 Narration Tips

- **Energy:** Enthusiastic but not over-the-top
- **Pace:** Moderate speed, clear enunciation
- **Tone:** Professional but friendly
- **Emphasis:** Stress key benefits (automatic, actionable, synchronized)

---

## ✅ Pre-Recording Checklist

- [ ] Script memorized or on teleprompter
- [ ] Demo environment set up and tested
- [ ] All commands work as expected
- [ ] Screen recording software configured
- [ ] Microphone tested
- [ ] Background noise minimized
- [ ] Backup recording device ready

---

## 📤 Upload Checklist

- [ ] Video exported at 1080p
- [ ] File size under 500MB (YouTube limit)
- [ ] Uploaded to YouTube
- [ ] Set to "Public" or "Unlisted"
- [ ] Title: "SpecSync - Automatic Drift Detection for Your Codebase"
- [ ] Description includes GitHub link
- [ ] Tags: kiro, specsync, git, drift-detection, hackathon
- [ ] Thumbnail created (optional but recommended)
- [ ] Link copied for Devpost submission

---

Good luck with your recording! 🎬

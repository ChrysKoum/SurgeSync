# Kiroween Hackathon Submission Checklist for SpecSync

## 🎯 Submission Deadline
**Friday, December 5, 2025 (2:00 pm Pacific Time)**

---

## ✅ Required Components

### 1. **MCP Server Publication** ✓ CRITICAL
- [ ] **Publish MCP server to npm**
  - Package name: `@specsync/mcp-server` or similar
  - Must be publicly accessible
  - Include installation instructions
  
- [ ] **Test MCP installation**
  ```bash
  npx @specsync/mcp-server
  ```

- [ ] **MCP Configuration Documentation**
  - How to add to Kiro's mcp.json
  - Example configuration
  - Usage instructions

**Current Status:** MCP code exists in `mcp/` folder but NOT published to npm yet

---

### 2. **Open Source Repository** ✓ CRITICAL

- [ ] **Repository is PUBLIC on GitHub**
  - URL: https://github.com/[your-username]/specsync
  
- [ ] **Add OSI-Approved Open Source License**
  - Recommended: MIT License
  - Must be visible in "About" section
  - File: `LICENSE` at root
  
- [ ] **Include `.kiro` directory in repo**
  - ⚠️ DO NOT add to .gitignore
  - Must show: specs, hooks, steering usage
  - Current: `.kiro/specs/`, `.kiro/steering/`, `.kiro/settings/`

- [ ] **Verify .gitignore doesn't exclude .kiro**
  ```bash
  # Check current .gitignore
  cat .gitignore | grep -i kiro
  # Should return nothing or commented lines
  ```

**Current Status:** Repo exists locally, needs to be pushed to GitHub with proper license

---

### 3. **Demo Video** ✓ CRITICAL

- [ ] **Create 3-minute demo video**
  - Show SpecSync in action
  - Demonstrate key features
  - Show Kiro integration
  
- [ ] **Upload to YouTube/Vimeo**
  - Make publicly visible
  - Get shareable link
  
- [ ] **Video must show:**
  - Installing SpecSync
  - Making a code change
  - Validation running
  - Drift detection
  - Task/suggestion generation
  - How Kiro was used to build it

**Suggested Script:**
```
0:00-0:30 - Introduction & Problem
0:30-1:00 - Installation & Setup
1:00-2:00 - Live Demo (commit with drift)
2:00-2:30 - Show validation, tasks, suggestions
2:30-3:00 - Kiro integration & conclusion
```

---

### 4. **Project Description** ✓ CRITICAL

- [ ] **Write compelling description on Devpost**
  - What is SpecSync?
  - What problem does it solve?
  - How does it work?
  - Why is it valuable?

**Template:**
```markdown
# SpecSync - Keep Your Specs, Code, Tests & Docs in Perfect Sync

## The Problem
Developers constantly face drift between specifications, code, tests, and documentation. 
Changes in one area don't automatically update others, leading to:
- Integration bugs
- Outdated documentation
- Missing tests
- Wasted time

## The Solution
SpecSync is a commit-time quality gate that automatically:
- Detects drift between specs, code, tests, and docs
- Generates actionable tasks to fix issues
- Validates alignment before commits
- Keeps everything synchronized

## How It Works
1. Install SpecSync pre-commit hook
2. Make code changes
3. Commit triggers validation
4. SpecSync detects any drift
5. Get specific tasks to fix issues
6. Commit proceeds with tasks generated

## Key Features
- 🔍 Automatic drift detection
- 📋 Task generation for fixes
- 🎯 Steering rules for customization
- 🔄 Three modes: blocking, tasks, auto-fix
- 🌉 Cross-repo sync (future)

## Built With Kiro
[Detailed explanation of Kiro usage - see section 6 below]
```

---

### 5. **Category Selection** ✓ REQUIRED

Choose ONE primary category:

- [ ] **Resurrection** - Bringing back spec-driven development
- [ ] **Frankenstein** - Stitching together git hooks + MCP + validation
- [ ] **Skeleton Crew** - NOT APPLICABLE (requires 2 apps)
- [ ] **Costume Contest** - NOT APPLICABLE (UI not the focus)

**Recommended: Frankenstein** ✅
- Combines git hooks, MCP tools, Python validation, TypeScript MCP
- "Stitches together" multiple technologies into one cohesive system

**Alternative: Resurrection** ✅
- Brings back the "lost art" of spec-driven development
- Modernizes it with AI and automation

---

### 6. **Kiro Usage Write-Up** ✓ CRITICAL

Must explain HOW you used Kiro to build SpecSync:

- [ ] **Vibe Coding**
  ```markdown
  ## Vibe Coding
  - Used Kiro to generate initial validation logic
  - Structured conversations around "detect drift between X and Y"
  - Most impressive: Kiro generated the entire drift detection algorithm
    including AST parsing and comparison logic in one session
  - Iteratively refined through natural language descriptions
  ```

- [ ] **Specs**
  ```markdown
  ## Spec-Driven Development
  - Created comprehensive spec in .kiro/specs/specsync-core/
  - Kiro implemented features directly from requirements
  - Spec-driven approach ensured complete feature coverage
  - Compared to vibe coding: More structured, better for complex features
  ```

- [ ] **Steering Docs**
  ```markdown
  ## Steering Documents
  - Created .kiro/steering/rules.md for project conventions
  - Guided Kiro to follow specific patterns (EARS requirements, etc.)
  - Strategy: Define file correlation patterns upfront
  - Biggest difference: Consistent code style across all modules
  ```

- [ ] **Agent Hooks**
  ```markdown
  ## Agent Hooks
  - Created pre-commit hook that triggers validation
  - Automated workflow: commit → validate → generate tasks
  - Improved process: Caught drift before it entered codebase
  ```

- [ ] **MCP**
  ```markdown
  ## Model Context Protocol
  - Built custom MCP tool for git context extraction
  - Enabled Kiro to read staged changes automatically
  - Without MCP: Would need manual copy-paste of diffs
  - MCP made the workflow seamless and automatic
  ```

---

### 7. **Testing Instructions** ✓ REQUIRED

- [ ] **Provide clear setup instructions**
  ```markdown
  ## Installation
  
  1. Clone the repository
  2. Install dependencies:
     ```bash
     pip install -r requirements.txt
     cd mcp && npm install
     ```
  3. Install the pre-commit hook:
     ```bash
     python install_hook.py
     ```
  4. Configure MCP in Kiro (see MCP_SETUP.md)
  
  ## Testing
  
  1. Make a code change:
     ```bash
     vim backend/handlers/user.py
     # Add a new endpoint
     ```
  
  2. Commit the change:
     ```bash
     git add backend/handlers/user.py
     git commit -m "Add new endpoint"
     ```
  
  3. Observe SpecSync validation
  
  4. Check generated tasks:
     ```bash
     cat .kiro/specs/app/remediation-tasks.md
     ```
  ```

---

### 8. **Website/Landing Page** (Optional but Recommended)

- [ ] **Create simple landing page**
  - Explain what SpecSync is
  - Show demo video
  - Link to GitHub
  - Installation instructions
  
- [ ] **Options:**
  - GitHub Pages (free, easy)
  - Vercel/Netlify (free tier)
  - Simple HTML page in repo

**Minimal Landing Page Structure:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>SpecSync - Keep Your Code Aligned</title>
</head>
<body>
    <h1>SpecSync</h1>
    <p>Automatic drift detection for specs, code, tests & docs</p>
    
    <h2>Demo Video</h2>
    <iframe src="[YOUTUBE_LINK]"></iframe>
    
    <h2>Get Started</h2>
    <pre>pip install specsync</pre>
    
    <h2>Links</h2>
    <a href="[GITHUB_LINK]">GitHub</a>
    <a href="[DEVPOST_LINK]">Devpost</a>
</body>
</html>
```

---

### 9. **Documentation Files** ✓ REQUIRED

Ensure these exist and are up-to-date:

- [ ] **README.md** - Main project overview
- [ ] **INSTALLATION.md** or section in README
- [ ] **USER_GUIDE.md** - How to use SpecSync
- [ ] **MCP_SETUP.md** - How to configure MCP
- [ ] **ARCHITECTURE.md** - System design (already exists)
- [ ] **LICENSE** - Open source license

---

### 10. **Devpost Submission Form** ✓ FINAL STEP

- [ ] **Register on kiro.devpost.com**
- [ ] **Click "Submit Project"**
- [ ] **Fill out all fields:**
  - Project name: SpecSync
  - Tagline: "Keep your specs, code, tests & docs in perfect sync"
  - Description: [From section 4]
  - Demo video URL: [YouTube link]
  - GitHub repository URL: [Public repo]
  - Category: [Frankenstein or Resurrection]
  - Kiro usage write-up: [From section 6]
  - Built with: Python, TypeScript, FastAPI, Node.js, Git Hooks, MCP
  
- [ ] **Submit before deadline!**

---

## 🚀 Priority Action Items (Do These First)

### HIGH PRIORITY (Must Do)

1. **Publish MCP to npm** ⚠️ CRITICAL
   ```bash
   cd mcp
   npm publish --access public
   ```

2. **Add LICENSE file** ⚠️ CRITICAL
   ```bash
   # Add MIT License to root
   ```

3. **Push to GitHub** ⚠️ CRITICAL
   ```bash
   git remote add origin https://github.com/[username]/specsync
   git push -u origin main
   ```

4. **Verify .kiro not in .gitignore** ⚠️ CRITICAL
   ```bash
   # Check and remove if present
   ```

5. **Create demo video** ⚠️ CRITICAL
   - Record 3-minute walkthrough
   - Upload to YouTube
   - Get link

### MEDIUM PRIORITY (Should Do)

6. **Write Kiro usage section**
   - Document how you used each Kiro feature
   - Be specific with examples

7. **Polish README**
   - Clear installation steps
   - Usage examples
   - Screenshots/GIFs

8. **Test installation from scratch**
   - Clone repo in new directory
   - Follow your own instructions
   - Fix any issues

### LOW PRIORITY (Nice to Have)

9. **Create landing page**
   - Simple GitHub Pages site
   - Embed demo video

10. **Add screenshots to README**
    - Validation output
    - Task generation
    - Drift detection

---

## 📋 Pre-Submission Checklist

Before clicking "Submit" on Devpost:

- [ ] Repository is public
- [ ] LICENSE file exists and is visible
- [ ] .kiro directory is in repo (not gitignored)
- [ ] MCP is published to npm
- [ ] Demo video is uploaded and public
- [ ] README has installation instructions
- [ ] All tests pass
- [ ] Kiro usage is documented
- [ ] Category is selected
- [ ] Description is compelling

---

## 🎬 Demo Video Script

**Title:** "SpecSync - Automatic Drift Detection for Your Codebase"

**Script:**
```
[0:00-0:15] Introduction
"Hi, I'm [name] and this is SpecSync - a tool that keeps your 
specifications, code, tests, and documentation perfectly synchronized."

[0:15-0:30] The Problem
"Every developer knows this pain: you update your code, but forget to 
update the tests. Or you add a new API endpoint but the docs are outdated. 
This is called drift, and it causes bugs."

[0:30-1:00] The Solution
"SpecSync solves this by running automatically on every commit. 
Let me show you. Here's a FastAPI project with a spec file that 
defines our API endpoints."

[1:00-1:30] Live Demo - Part 1
"I'm going to add a new endpoint to get user posts. Watch what happens 
when I commit... SpecSync detects that this endpoint isn't in the spec, 
there are no tests, and the documentation is missing."

[1:30-2:00] Live Demo - Part 2
"Instead of blocking my commit, SpecSync generates specific tasks to fix 
each issue. It tells me exactly what to add to the spec, what tests to 
write, and what documentation to update."

[2:00-2:30] Kiro Integration
"I built SpecSync using Kiro's spec-driven development, MCP tools for 
git integration, and steering docs to maintain code quality. Kiro helped 
me generate the drift detection logic and validation engine."

[2:30-3:00] Conclusion
"SpecSync catches drift before it enters your codebase, generates 
actionable tasks, and keeps your team aligned. Check out the GitHub 
repo to try it yourself. Thanks!"
```

---

## 📞 Support

If you have questions:
- Hackathon support: support@devpost.com
- Submission deadline: December 5, 2025, 2:00 PM PT

---

## 🏆 Bonus Prizes You Can Enter

### Blog Post Prize ($100 each, first 50)
- [ ] Write blog post about SpecSync
- [ ] Post on https://dev.to/kirodotdev
- [ ] Use hashtag #kiro

### Social Blitz Prize ($100 each, 5 winners)
- [ ] Post on X/LinkedIn/Instagram/BlueSky
- [ ] Tag @kirodotdev
- [ ] Use hashtag #hookedonkiro
- [ ] Describe favorite thing about Kiro

---

## ⏰ Timeline Suggestion

**Week 1 (Now - Nov 29):**
- Publish MCP to npm
- Add LICENSE
- Push to GitHub
- Verify .kiro directory

**Week 2 (Dec 2-4):**
- Create demo video
- Write Kiro usage section
- Polish documentation
- Test installation

**Week 3 (Dec 5 - DEADLINE):**
- Submit on Devpost
- Write blog post (bonus)
- Post on social (bonus)

---

**Good luck! 🎃👻**

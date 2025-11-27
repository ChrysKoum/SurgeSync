# Publishing Guide for Hackathon Submission

## Step 1: Publish MCP to npm

```bash
# 1. Navigate to MCP directory
cd mcp

# 2. Build the TypeScript code
npm run build

# 3. Login to npm (if not already logged in)
npm login

# 4. Publish to npm
npm publish --access public

# 5. Verify publication
npm view @specsync/mcp-git-context
```

## Step 2: Push to GitHub

```bash
# 1. Create GitHub repo (on github.com)
# Name: specsync
# Description: Keep your specs, code, tests & docs in perfect sync
# Public: YES
# License: MIT

# 2. Add remote
git remote add origin https://github.com/chryskoum/specsync.git

# 3. Verify .kiro is NOT in .gitignore
cat .gitignore | grep -i kiro
# Should return nothing

# 4. Add all files
git add .

# 5. Commit
git commit -m "Initial commit for Kiroween Hackathon"

# 6. Push
git push -u origin main
```

## Step 3: Enable GitHub Pages

1. Go to repo Settings
2. Click "Pages" in sidebar
3. Source: Deploy from branch
4. Branch: main
5. Folder: /docs
6. Save

Your site will be at: `https://chryskoum.github.io/specsync/`

## Step 4: Update Links

Replace `chryskoum` and `YOUR_VIDEO_ID` in:
- `docs/index.html`
- `mcp/package.json`
- `mcp/README.md`
- `README.md`

## Step 5: Record Demo Video

Follow `DEMO_VIDEO_SCRIPT.md` and upload to YouTube

## Step 6: Submit on Devpost

1. Go to kiro.devpost.com
2. Click "Submit Project"
3. Fill in all fields
4. Submit before December 5, 2025 2:00 PM PT

Done! 🎉

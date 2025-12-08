# Setup GitHub Repository - Step by Step

## Step 1: Initialize Git Repository

```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI
git init
```

## Step 2: Add All Files

```bash
git add .
```

## Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: backrAI Leverage Engine v1.1"
```

## Step 4: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `backrAI` (or your preferred name)
3. Description: "Universal attribution layer for the creator economy"
4. Choose: **Private** (recommended) or **Public**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 5: Connect and Push

After creating the repo, GitHub will show you commands. Use these:

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/backrAI.git

# Or if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/backrAI.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 6: Verify

Go to your GitHub repository and verify all files are there.

## Important Notes

### Before Pushing:

1. **Check for sensitive data:**
   - Make sure `.env` files are in `.gitignore` ✅
   - No API keys or secrets in code
   - Database credentials should be in `.env` (not committed)

2. **Review what's being committed:**
   ```bash
   git status
   ```

3. **If you see sensitive files:**
   ```bash
   git reset HEAD <file>
   # Then add to .gitignore
   ```

### Files That Should NOT Be Committed:

- `.env` files (already in .gitignore)
- `node_modules/` (already in .gitignore)
- `venv/` (already in .gitignore)
- `.plasmo/` build folders (already in .gitignore)
- `.next/` build folders (already in .gitignore)

## Quick Commands Summary

```bash
cd /Users/nestoraldreteochoa/Documents/Documents/Dev/backrAI
git init
git add .
git commit -m "Initial commit: backrAI Leverage Engine v1.1"
git remote add origin https://github.com/YOUR_USERNAME/backrAI.git
git branch -M main
git push -u origin main
```

## Troubleshooting

### If you get "remote origin already exists":
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/backrAI.git
```

### If you need to update .gitignore:
```bash
# Edit .gitignore, then:
git rm -r --cached .
git add .
git commit -m "Update .gitignore"
```

### If push is rejected:
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```


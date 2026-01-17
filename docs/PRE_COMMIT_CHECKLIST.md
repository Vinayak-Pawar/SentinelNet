# Pre-Commit Checklist ✓

Use this checklist before every commit to ensure repository security.

---

## 🔒 Security Checks

- [ ] **Run security script:**
  ```bash
  ./scripts/pre-commit-check.sh
  ```

- [ ] **No .env files staged:**
  ```bash
  git status | grep -E "\.env$"
  # Should return nothing
  ```

- [ ] **No credential files staged:**
  ```bash
  git status | grep -E "(\.pem|\.key|credentials\.json)"
  # Should return nothing
  ```

- [ ] **No database files staged:**
  ```bash
  git status | grep -E "\.(db|sqlite)$"
  # Should return nothing
  ```

- [ ] **No log files staged:**
  ```bash
  git status | grep -E "\.log$"
  # Should return nothing
  ```

---

## 📋 Content Review

- [ ] **Review staged changes:**
  ```bash
  git diff --staged
  ```

- [ ] **Check for hardcoded secrets:**
  ```bash
  git diff --staged | grep -i -E "(password|api_key|secret|token)" | grep "="
  ```

- [ ] **Verify file list:**
  ```bash
  git status
  ```

- [ ] **Check file sizes:**
  ```bash
  git diff --cached --name-only | xargs ls -lh
  ```

---

## 📝 Code Quality

- [ ] **Files are properly formatted:**
  ```bash
  black sentinelnet/
  isort sentinelnet/
  ```

- [ ] **No syntax errors:**
  ```bash
  python -m py_compile sentinelnet/**/*.py
  ```

- [ ] **Tests pass (if applicable):**
  ```bash
  pytest tests/ -v
  ```

---

## 📚 Documentation

- [ ] **README updated** (if needed)
- [ ] **ROADMAP updated** (tasks marked complete)
- [ ] **Commit message is descriptive**
- [ ] **Comments added** for complex code

---

## ✅ Final Steps

1. **Stage changes:**
   ```bash
   git add .
   ```

2. **Final review:**
   ```bash
   git status
   git diff --staged --stat
   ```

3. **Commit with message:**
   ```bash
   git commit -m "type: description
   
   - Detail 1
   - Detail 2
   "
   ```
   
   **Commit types:**
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation
   - `refactor:` Code refactoring
   - `test:` Tests
   - `chore:` Maintenance

4. **Push to GitHub:**
   ```bash
   git push origin main
   ```

---

## 🚨 If Something Goes Wrong

### Accidentally staged a secret:
```bash
# Remove from staging
git reset HEAD path/to/file

# Add to .gitignore
echo "path/to/file" >> .gitignore
```

### Already committed but not pushed:
```bash
# Remove from last commit
git reset --soft HEAD~1

# Remove the file
rm path/to/secret/file

# Stage other files
git add .

# Commit again
git commit -m "your message"
```

### Already pushed to GitHub:
1. **Immediately rotate credentials**
2. **Contact security team**
3. **Use BFG Repo-Cleaner** to remove from history
4. **Force push** (if team allows)

---

## 💡 Quick Commands

### See what's ignored:
```bash
git status --ignored
```

### Check if file would be ignored:
```bash
git check-ignore -v filename
```

### See all tracked files:
```bash
git ls-files
```

### Clean untracked files (careful!):
```bash
git clean -n  # Preview
git clean -f  # Execute
```

---

**Print this checklist or keep it open during commits!**

*Last updated: January 17, 2026*

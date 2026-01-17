# .gitignore Configuration Guide

This document explains what's excluded from Git and why.

---

## 🔒 Critical Security Exclusions

### Environment Files
```
.env
.env.*
```
**Why:** Contains API keys, database passwords, cloud credentials  
**⚠️ NEVER commit these files!**

### Cloud Credentials
```
service-account-key.json
*-credentials.json
gcp-*.json
azure-*.json
*.pem
*.key
```
**Why:** Cloud provider authentication keys and certificates  
**⚠️ Exposing these could compromise your cloud resources!**

---

## 💾 Database Files

### SQLite Databases
```
*.db
*.sqlite
*.sqlite3
data/sentinelnet.db
```
**Why:** 
- Contains runtime data (alerts, incidents)
- Can be large
- Local development data shouldn't be in repo
- Each developer should have their own database

**Note:** Empty `data/` directory IS tracked via `.gitkeep`

---

## 📝 Logs and Monitoring Data

### Application Logs
```
logs/*.log
*.log
```
**Why:** 
- Can become very large
- Contains runtime information
- Different on each machine

**Note:** `logs/.gitkeep` ensures directory structure is preserved

### Prometheus/Grafana Data
```
prometheus_data/
grafana_data/
```
**Why:** Time-series data can be huge and is environment-specific

---

## 🧪 Testing and Development

### Test Databases
```
tests/fixtures/*.db
tests/fixtures/*.sqlite
```
**Why:** Test data generated during test runs

### Cache Files
```
.pytest_cache/
.cache/
__pycache__/
*.pyc
```
**Why:** Python bytecode and test caches (auto-generated)

---

## 🎯 Python-Specific

### Virtual Environments
```
venv/
env/
.venv/
sentinelnet_env/
```
**Why:** Each developer creates their own environment

### Package Build Artifacts
```
dist/
build/
*.egg-info/
```
**Why:** Generated during `pip install` or builds

### UV Package Manager
```
.uv/
uv.lock
```
**Why:** UV cache and lock files (can be regenerated)

---

## 💻 IDE and Editor Files

### VSCode/Cursor
```
.vscode/
.cursor/
```
**Why:** Personal editor settings  
**Note:** Consider keeping if team wants shared settings

### PyCharm
```
.idea/
*.iml
```
**Why:** PyCharm project files

### Vim/Emacs
```
*.swp
*.swo
*~
```
**Why:** Temporary editor files

---

## 🍎 MacOS Files

```
.DS_Store
._*
.AppleDouble
.Spotlight-V100
```
**Why:** MacOS system files that shouldn't be in Git

---

## 🚀 CI/CD and Infrastructure

### Terraform State
```
*.tfstate
*.tfstate.*
.terraform/
```
**Why:** 
- Contains sensitive infrastructure state
- Should be stored in remote backend (S3, etc.)

### Docker Overrides
```
docker-compose.override.yml
```
**Why:** Personal docker configurations  
**Note:** Keep `docker-compose.override.yml.example` as template

---

## 📊 Large Files

### Model Files
```
models/*.pkl
models/*.joblib
models/*.h5
models/*.pt
```
**Why:** ML models can be 100MB+  
**Solution:** Use Git LFS or cloud storage

### Media Files
```
*.mp4
*.avi
*.mov
```
**Why:** Video files are large  
**Solution:** Store in cloud bucket if needed

---

## ✅ What IS Committed

### Source Code
- ✅ All `.py` files in `sentinelnet/`
- ✅ Configuration files (`pyproject.toml`, `requirements.txt`)
- ✅ Documentation (`docs/*.md`, `README.md`)
- ✅ Tests (`tests/*.py`)

### Directory Structure
- ✅ `data/.gitkeep` (preserves directory)
- ✅ `logs/.gitkeep` (preserves directory)
- ✅ `models/.gitkeep` (preserves directory)

### Configuration Examples
- ✅ `.env.example` (template for `.env`)
- ✅ `docker-compose.yml` (not the override)
- ✅ `setup_and_run_v2.sh` (setup script)

---

## 🛡️ Security Best Practices

### Before Committing

1. **Check for secrets:**
   ```bash
   git diff --staged
   ```

2. **Verify .env is ignored:**
   ```bash
   git status | grep .env
   # Should return nothing
   ```

3. **Check for large files:**
   ```bash
   find . -size +10M -not -path "./.git/*"
   ```

### If You Accidentally Commit Secrets

```bash
# Remove from history (use with caution!)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/secret/file' \
  --prune-empty --tag-name-filter cat -- --all

# Or use BFG Repo-Cleaner (recommended)
# https://rtyley.github.io/bfg-repo-cleaner/
```

**Then:**
1. Rotate all exposed credentials immediately
2. Update API keys
3. Review access logs

---

## 📋 Quick Reference

### Check what will be committed:
```bash
git status
git diff --staged
```

### See what's ignored:
```bash
git status --ignored
```

### Test if file would be ignored:
```bash
git check-ignore -v filename
```

### Force add an ignored file (if needed):
```bash
git add -f filename
```

---

## 🔍 Common Issues

### "I need to commit a .env file"
**Don't!** Instead:
1. Create `.env.example` with dummy values
2. Document required keys in README
3. Have developers copy `.env.example` to `.env`

### "Database file is too big for GitHub"
**Solution:**
- Keep databases in `.gitignore` ✅
- Use migrations or seed scripts instead
- Store sample data as JSON/CSV if needed

### "Want to track some log files"
**Solution:**
```bash
# Add exception to .gitignore
!logs/important.log

# Then commit
git add logs/important.log
```

---

## 📚 Additional Resources

- [GitHub .gitignore templates](https://github.com/github/gitignore)
- [Git LFS for large files](https://git-lfs.github.com/)
- [git-secrets tool](https://github.com/awslabs/git-secrets)

---

**Last Updated:** January 17, 2026  
**Maintained by:** SentinelNet Team

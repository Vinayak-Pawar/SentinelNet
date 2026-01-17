#!/bin/bash
# Pre-commit security check script
# Run this before committing to ensure no secrets are accidentally committed

echo "======================================================================"
echo "🔒 SentinelNet Pre-Commit Security Check"
echo "======================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ISSUES_FOUND=0

# Function to check for patterns
check_pattern() {
    local pattern=$1
    local description=$2
    
    echo "Checking for: $description"
    
    RESULTS=$(git diff --cached --name-only | xargs grep -l "$pattern" 2>/dev/null || true)
    
    if [ ! -z "$RESULTS" ]; then
        echo -e "${RED}❌ FOUND: $description in:${NC}"
        echo "$RESULTS" | sed 's/^/   /'
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✅ OK${NC}"
    fi
    echo ""
}

# Check for common secret patterns
echo "Scanning staged files for secrets..."
echo ""

check_pattern "AKIA[0-9A-Z]{16}" "AWS Access Key"
check_pattern "[a-f0-9]{40}" "AWS Secret Key (potential)"
check_pattern "sk-[a-zA-Z0-9]{48}" "OpenAI API Key"
check_pattern "AIza[0-9A-Za-z\\-_]{35}" "Google API Key"
check_pattern "ya29\.[0-9A-Za-z\\-_]+" "Google OAuth Token"
check_pattern "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}" "UUID (potential secret)"
check_pattern "password\s*=\s*['\"][^'\"]+['\"]" "Hardcoded Password"
check_pattern "api_key\s*=\s*['\"][^'\"]+['\"]" "Hardcoded API Key"
check_pattern "secret\s*=\s*['\"][^'\"]+['\"]" "Hardcoded Secret"
check_pattern "token\s*=\s*['\"][^'\"]+['\"]" "Hardcoded Token"

# Check for specific files that should never be committed
echo "======================================================================"
echo "Checking for sensitive files..."
echo ""

SENSITIVE_FILES=(
    ".env"
    ".env.local"
    ".env.production"
    "service-account-key.json"
    "*.pem"
    "*.key"
    "*-credentials.json"
    "*.db"
    "*.sqlite"
)

for pattern in "${SENSITIVE_FILES[@]}"; do
    FILES=$(git diff --cached --name-only | grep -E "$pattern" || true)
    if [ ! -z "$FILES" ]; then
        echo -e "${RED}❌ FOUND sensitive file: $pattern${NC}"
        echo "$FILES" | sed 's/^/   /'
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
done

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ No sensitive files found${NC}"
fi

echo ""

# Check file sizes
echo "======================================================================"
echo "Checking for large files (>10MB)..."
echo ""

LARGE_FILES=$(git diff --cached --name-only | xargs du -h 2>/dev/null | awk '$1 ~ /[0-9]+M/ && $1+0 > 10 {print $2}' || true)

if [ ! -z "$LARGE_FILES" ]; then
    echo -e "${YELLOW}⚠️  Large files found (consider Git LFS):${NC}"
    echo "$LARGE_FILES" | sed 's/^/   /'
    echo ""
    echo -e "${YELLOW}Consider using Git LFS for files >10MB${NC}"
else
    echo -e "${GREEN}✅ No large files found${NC}"
fi

echo ""

# Summary
echo "======================================================================"
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}🎉 Security check PASSED! Safe to commit.${NC}"
    echo ""
    echo "Next steps:"
    echo "  git commit -m 'your message'"
    echo "  git push origin main"
    exit 0
else
    echo -e "${RED}🚨 Security check FAILED! Found $ISSUES_FOUND potential issues.${NC}"
    echo ""
    echo "Actions required:"
    echo "  1. Remove sensitive files: git reset HEAD <file>"
    echo "  2. Add to .gitignore"
    echo "  3. Rotate any exposed credentials"
    echo "  4. Run this script again"
    exit 1
fi

#!/bin/bash
set -e

echo "Building your-submission.zip..."

# Ensure output exists (we will package output_test as output if output doesn't exist, to accommodate the local run)
if [ ! -d "output" ] && [ -d "output_test" ]; then
    cp -r output_test output
fi

# Clean up old zip
rm -f your-submission.zip

# Create zip file excluding unwanted directories and files
zip -r your-submission.zip source/ output/ \
    -x "source/.env" \
    -x "source/cache/*" \
    -x "source/audit/*" \
    -x "source/usage_report.json" \
    -x "*/__pycache__/*" \
    -x "*/.pytest_cache/*" \
    -x "train/bills/*" \
    -x "test/bills/*" \
    -x "tests/fixtures/*" \
    -x "venv/*" \
    -x ".env" \
    -x "cache/*" \
    -x "audit/*" \
    -x "usage_report.json"

echo ""
echo "=== Zip Contents ==="
unzip -l your-submission.zip

echo ""
echo "=== File Size Check ==="
SIZE=$(stat -c%s your-submission.zip 2>/dev/null || stat -f%z your-submission.zip 2>/dev/null)
SIZE_MB=$(echo "scale=2; $SIZE/1048576" | bc 2>/dev/null || awk -v size="$SIZE" 'BEGIN {printf "%.2f", size/1048576}')

echo "Size: $SIZE_MB MB"

if (( $(echo "$SIZE_MB > 15.0" | bc -l 2>/dev/null || awk -v size="$SIZE" 'BEGIN {if (size > 15728640) print 1; else print 0}') )); then
    echo "[FAIL] Zip file exceeds 15 MB."
    exit 1
else
    echo "[PASS] Zip file is under 15 MB."
fi

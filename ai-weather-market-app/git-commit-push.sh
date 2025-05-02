#!/bin/bash

# Script to add all changes, commit each file individually, and push to origin main
# Improved version with error handling and checks for no changes, including untracked files
# Displays count of changes committed successfully and failed commits
# Limits commit to 150000 files per run

MAX_FILES=150000

# Get list of modified files
modified_files=$(git status --porcelain | grep -E '^[ M]' | awk '{print $2}')

# Get list of untracked files
untracked_files=$(git ls-files --others --exclude-standard)

# Combine modified and untracked files
files="$modified_files
$untracked_files"

# Remove empty lines
files=$(echo "$files" | sed '/^$/d')

# Limit to MAX_FILES
files_to_commit=$(echo "$files" | head -n $MAX_FILES)

# Check if there are any changes
if [ -z "$files_to_commit" ]; then
  echo "No changes to commit."
  exit 0
fi

commit_count=0
fail_count=0

# Commit each file individually
for file in $files_to_commit; do
  echo "Adding $file"
  git add "$file"
  # Check if file has staged changes
  if ! git diff --cached --quiet -- "$file"; then
    echo "Committing $file"
    if git commit -m "Commit $file"; then
      commit_count=$((commit_count + 1))
    else
      echo "Failed to commit $file"
      fail_count=$((fail_count + 1))
    fi
  else
    echo "No changes to commit for $file"
  fi
done

# Push commits to origin main
if ! git push origin main; then
  echo "Failed to push to origin main"
  exit 1
fi

echo "All changes processed."
echo "Total files committed successfully: $commit_count"
echo "Total files failed to commit: $fail_count"
echo "Committed up to $MAX_FILES files in this run. Run the script again to commit remaining changes."
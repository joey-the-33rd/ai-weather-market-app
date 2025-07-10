#!/bin/bash
# Improved script to untrack all files currently tracked by git but matching .gitignore patterns
# Supports dry-run mode and confirmation prompt

set -e

usage() {
  echo "Usage: $0 [-n|--dry-run] [-y|--yes]"
  echo "  -n, --dry-run   Show files to be untracked without actually untracking"
  echo "  -y, --yes       Skip confirmation prompt"
  exit 1
}

dry_run=false
auto_yes=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -n|--dry-run)
      dry_run=true
      shift
      ;;
    -y|--yes)
      auto_yes=true
      shift
      ;;
    *)
      usage
      ;;
  esac
done

echo "Finding tracked files that match .gitignore patterns..."

ignored_files=()
while IFS= read -r file; do
  if git check-ignore -q "$file"; then
    ignored_files+=("$file")
  fi
done < <(git ls-files)

if [ ${#ignored_files[@]} -eq 0 ]; then
  echo "No tracked files match .gitignore patterns. Nothing to untrack."
  exit 0
fi

echo "Tracked files matching .gitignore patterns:"
printf '%s\n' "${ignored_files[@]}"

if [ "$dry_run" = true ]; then
  echo "Dry run mode enabled. No files will be untracked."
  exit 0
fi

if [ "$auto_yes" = false ]; then
  read -p "Do you want to untrack these files? [y/N] " confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Aborted by user."
    exit 1
  fi
fi

echo "Untracking files..."
git rm --cached "${ignored_files[@]}"

echo "Done. Please commit the changes to finalize untracking."

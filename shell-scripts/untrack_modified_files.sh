#!/bin/bash
# Script to untrack all files currently modified or staged but not committed
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

echo "Finding modified and staged files..."

modified_files=()
while IFS= read -r file; do
  modified_files+=("$file")
done < <(git ls-files -m)

staged_files=()
while IFS= read -r file; do
  staged_files+=("$file")
done < <(git diff --name-only --cached)

# Combine and unique files
all_files=($(printf "%s\n" "${modified_files[@]}" "${staged_files[@]}" | sort -u))

if [ ${#all_files[@]} -eq 0 ]; then
  echo "No modified or staged files to untrack."
  exit 0
fi

echo "Files to be untracked:"
printf '%s\n' "${all_files[@]}"

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
git rm --cached "${all_files[@]}"

echo "Done. Please commit the changes to finalize untracking."

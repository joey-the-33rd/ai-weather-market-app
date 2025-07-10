#!/bin/bash
# Script to unstage all files currently staged in git
# Supports dry-run mode and confirmation prompt

set -e

usage() {
  echo "Usage: $0 [-n|--dry-run] [-y|--yes]"
  echo "  -n, --dry-run   Show files to be unstaged without actually unstaging"
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

echo "Finding staged files..."

staged_files=()
while IFS= read -r file; do
  staged_files+=("$file")
done < <(git diff --name-only --cached)

if [ ${#staged_files[@]} -eq 0 ]; then
  echo "No staged files to unstage."
  exit 0
fi

echo "Files to be unstaged:"
printf '%s\n' "${staged_files[@]}"

if [ "$dry_run" = true ]; then
  echo "Dry run mode enabled. No files will be unstaged."
  exit 0
fi

if [ "$auto_yes" = false ]; then
  read -p "Do you want to unstage these files? [y/N] " confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Aborted by user."
    exit 1
  fi
fi

echo "Unstaging files..."
git reset "${staged_files[@]}"

echo "Done. The files have been unstaged."

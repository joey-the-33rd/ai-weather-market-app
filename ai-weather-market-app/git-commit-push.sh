#!/bin/bash

# Script to add all changes, commit each file individually, and push to origin main

# Get list of changed files
files=$(git status --porcelain | awk '{print $2}')

# Commit each file individually
for file in $files; do
  git add "$file"
  git commit -m "Commit $file"
done

# Push commits to origin main
git push origin main

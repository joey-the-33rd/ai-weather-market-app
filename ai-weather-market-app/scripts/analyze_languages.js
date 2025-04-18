const fs = require('fs');
const path = require('path');

const extensionsMap = {
  '.js': 'JavaScript',
  '.jsx': 'JavaScript',
  '.ts': 'TypeScript',
  '.tsx': 'TypeScript',
  '.py': 'Python',
  '.java': 'Java',
  '.kt': 'Kotlin',
  '.gradle': 'Groovy',
  '.json': 'JSON',
  '.html': 'HTML',
  '.css': 'CSS',
  '.scss': 'SCSS',
  '.md': 'Markdown',
  '.sh': 'Shell',
  '.yml': 'YAML',
  '.yaml': 'YAML',
  '.xml': 'XML',
  '.txt': 'Text',
  // add more extensions and languages as needed
};

function getAllFiles(dirPath, arrayOfFiles) {
  const files = fs.readdirSync(dirPath);

  arrayOfFiles = arrayOfFiles || [];

  files.forEach(function(file) {
    const fullPath = path.join(dirPath, file);
    if (fs.statSync(fullPath).isDirectory()) {
      arrayOfFiles = getAllFiles(fullPath, arrayOfFiles);
    } else {
      arrayOfFiles.push(fullPath);
    }
  });

  return arrayOfFiles;
}

function analyzeLanguages(rootDir) {
  const allFiles = getAllFiles(rootDir);
  const languageSizes = {};

  allFiles.forEach(file => {
    const ext = path.extname(file).toLowerCase();
    const language = extensionsMap[ext] || 'Other';
    const stats = fs.statSync(file);
    const size = stats.size;

    if (!languageSizes[language]) {
      languageSizes[language] = 0;
    }
    languageSizes[language] += size;
  });

  // Convert to array and sort by size descending
  const sortedLanguages = Object.entries(languageSizes)
    .map(([language, size]) => ({ language, size }))
    .sort((a, b) => b.size - a.size);

  return sortedLanguages;
}

const rootDir = path.resolve(__dirname, '..');
const result = analyzeLanguages(rootDir);

console.log("Language usage in the repository (by bytes):");
result.forEach(({ language, size }) => {
  console.log(`${language}: ${size} bytes`);
});

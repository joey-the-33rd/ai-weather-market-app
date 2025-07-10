module.exports = {
  transform: {
    "^.+\\.[tj]sx?$": "babel-jest"
  },
  transformIgnorePatterns: [
    "/node_modules/(?!axios)/"
  ],
  moduleFileExtensions: ["js", "jsx", "ts", "tsx", "json", "node"],
  testEnvironment: "jsdom",
  globals: {
    "babel-jest": {
      useESM: true
    }
  }
}

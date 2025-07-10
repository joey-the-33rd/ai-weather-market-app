/**
 * This file is for test setup, you can add global mocks or configurations here if needed
 */

// Mock ResizeObserver for tests to avoid ReferenceError
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

global.ResizeObserver = ResizeObserver;

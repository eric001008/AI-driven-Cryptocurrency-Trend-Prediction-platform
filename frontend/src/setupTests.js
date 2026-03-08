// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';
import fetchMock from 'jest-fetch-mock';
// src/setupTests.js

fetchMock.enableMocks();

// Mock ResizeObserver for components that use it (e.g., Chakra UI, Recharts)
global.ResizeObserver = class {
  constructor(_) {}

  observe() {}

  unobserve() {}

  disconnect() {}
};

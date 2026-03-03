// src/setupTests.js

// 1. Extend Vitest expect with jest-dom matchers (toBeInTheDocument, toHaveTextContent, etc.)
import '@testing-library/jest-dom/vitest';

// 2. Import only what we need from vitest (single import)
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// Auto-cleanup after each test (recommended for @testing-library/react)
afterEach(() => {
  cleanup();
});

// Polyfill TextEncoder / TextDecoder if missing (used by some router / encoding logic)
if (typeof globalThis.TextEncoder === 'undefined') {
  const { TextEncoder, TextDecoder } = await import('util');
  globalThis.TextEncoder = TextEncoder;
  globalThis.TextDecoder = TextDecoder;
}

// Mock window.matchMedia (very common for components using media queries / responsive design)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),           // legacy
    removeListener: vi.fn(),        // legacy
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  writable: true,
  value: {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  },
});

// Mock window.location (safer than delete + redefine)
vi.stubGlobal('location', {
  href: 'http://localhost:5173/',
  pathname: '/',
  origin: 'http://localhost:5173',
  assign: vi.fn(),
  replace: vi.fn(),
});

// Mock Vite env variables (consistent test environment)
vi.stubEnv('VITE_AUTH0_DOMAIN', 'test-domain.auth0.com');
vi.stubEnv('VITE_AUTH0_CLIENT_ID', 'test-client-id');
vi.stubEnv('VITE_AUTH0_CALLBACK_URL', 'http://localhost');
vi.stubEnv('VITE_AUTH0_AUDIENCE', 'https://test-api');
vi.stubEnv('VITE_SKIP_AUTH', 'true');
vi.stubEnv('DEV', true);

// Optional: clear mocks before each test (uncomment if you have flaky state)
// beforeEach(() => {
//   vi.clearAllMocks();
// });
import { vi, expect } from 'vitest';

// Alias jest to vi for compatibility with existing Jest-based tests
// This lets us keep jest.fn(), jest.mock(), etc. without rewriting every test file.
// Vitest's API is very similar, so most helpers map 1-to-1.
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
globalThis.jest = vi;
// Provide typed alias for TS when tests reference jest.MockedFunction
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
globalThis.jest.fn = vi.fn;
// For convenience map common functions that may be referenced
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
globalThis.jest.spyOn = vi.spyOn;

// Node 18+ provides global fetch; if running on older Node, consider uncommenting
// and adding a lightweight polyfill like `cross-fetch/polyfill`.

// You can place any other global test setup (e.g., mock server) here.

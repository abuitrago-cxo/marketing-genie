import { renderHook, act } from '@testing-library/react';
import { useUserPreferences, useTheme, useUIPreferences, useProjectPreferences } from '../useUserPreferences';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock document.documentElement
Object.defineProperty(document, 'documentElement', {
  value: {
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
    },
  },
  writable: true,
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

describe('useUserPreferences', () => {
  beforeEach(() => {
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
  });

  it('should load default preferences when localStorage is empty', async () => {
    localStorageMock.getItem.mockReturnValue(null);

    const { result } = renderHook(() => useUserPreferences());

    expect(result.current.preferences.theme).toBe('system');
    expect(result.current.preferences.colorScheme).toBe('original');
    expect(result.current.preferences.sidebarCollapsed).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should load preferences from localStorage', async () => {
    const storedPreferences = {
      theme: 'dark',
      colorScheme: 'enhanced',
      sidebarCollapsed: true,
      compactMode: true,
    };

    localStorageMock.getItem.mockReturnValue(JSON.stringify(storedPreferences));

    const { result } = renderHook(() => useUserPreferences());

    expect(result.current.preferences.theme).toBe('dark');
    expect(result.current.preferences.colorScheme).toBe('enhanced');
    expect(result.current.preferences.sidebarCollapsed).toBe(true);
    expect(result.current.preferences.compactMode).toBe(true);
  });

  it('should update preferences and save to localStorage', async () => {
    localStorageMock.getItem.mockReturnValue(null);

    const { result } = renderHook(() => useUserPreferences());

    act(() => {
      result.current.updatePreference('theme', 'dark');
    });

    expect(result.current.preferences.theme).toBe('dark');
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'userPreferences',
      expect.stringContaining('"theme":"dark"')
    );
  });

  it('should reset preferences', async () => {
    const storedPreferences = {
      theme: 'dark',
      sidebarCollapsed: true,
    };

    localStorageMock.getItem.mockReturnValue(JSON.stringify(storedPreferences));

    const { result } = renderHook(() => useUserPreferences());

    expect(result.current.preferences.theme).toBe('dark');

    act(() => {
      result.current.resetPreferences();
    });

    expect(result.current.preferences.theme).toBe('system');
    expect(result.current.preferences.sidebarCollapsed).toBe(false);
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('userPreferences');
  });

  it('should export preferences as JSON string', async () => {
    localStorageMock.getItem.mockReturnValue(null);

    const { result } = renderHook(() => useUserPreferences());

    const exported = result.current.exportPreferences();
    const parsed = JSON.parse(exported);

    expect(parsed.theme).toBe('system');
    expect(parsed.colorScheme).toBe('original');
  });

  it('should import preferences from JSON string', async () => {
    localStorageMock.getItem.mockReturnValue(null);

    const { result } = renderHook(() => useUserPreferences());

    const importData = JSON.stringify({
      theme: 'dark',
      colorScheme: 'enhanced',
      compactMode: true,
    });

    let importResult;
    act(() => {
      importResult = result.current.importPreferences(importData);
    });

    expect(importResult).toBe(true);
    expect(result.current.preferences.theme).toBe('dark');
    expect(result.current.preferences.colorScheme).toBe('enhanced');
    expect(result.current.preferences.compactMode).toBe(true);
  });

  it('should handle invalid import data', async () => {
    localStorageMock.getItem.mockReturnValue(null);

    const { result } = renderHook(() => useUserPreferences());

    let importResult;
    act(() => {
      importResult = result.current.importPreferences('invalid json');
    });

    expect(importResult).toBe(false);
    expect(result.current.error).toBe('Invalid preferences data');
  });
});

describe('useTheme', () => {
  beforeEach(() => {
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    (document.documentElement.classList.add as jest.Mock).mockClear();
    (document.documentElement.classList.remove as jest.Mock).mockClear();
  });

  it('should apply light theme', async () => {
    localStorageMock.getItem.mockReturnValue(null);

    const { result } = renderHook(() => useTheme());

    act(() => {
      result.current.setTheme('light');
    });

    expect(document.documentElement.classList.remove).toHaveBeenCalledWith('dark');
  });

  it('should apply dark theme', async () => {
    localStorageMock.getItem.mockReturnValue(null);

    const { result } = renderHook(() => useTheme());

    act(() => {
      result.current.setTheme('dark');
    });

    expect(document.documentElement.classList.add).toHaveBeenCalledWith('dark');
  });
});

describe('useUIPreferences', () => {
  it('should manage UI preferences', async () => {
    localStorageMock.getItem.mockReturnValue(null);

    const { result } = renderHook(() => useUIPreferences());

    expect(result.current.sidebarCollapsed).toBe(false);
    expect(result.current.compactMode).toBe(false);
    expect(result.current.animationsEnabled).toBe(true);

    act(() => {
      result.current.setSidebarCollapsed(true);
    });

    expect(result.current.sidebarCollapsed).toBe(true);

    act(() => {
      result.current.setCompactMode(true);
    });

    expect(result.current.compactMode).toBe(true);

    act(() => {
      result.current.setAnimationsEnabled(false);
    });

    expect(result.current.animationsEnabled).toBe(false);
  });
});

describe('useProjectPreferences', () => {
  it('should manage project preferences', async () => {
    localStorageMock.getItem.mockReturnValue(null);

    const { result } = renderHook(() => useProjectPreferences());

    expect(result.current.defaultProjectView).toBe('grid');
    expect(result.current.projectSortBy).toBe('updated');
    expect(result.current.showArchivedProjects).toBe(false);

    act(() => {
      result.current.setDefaultProjectView('list');
    });

    expect(result.current.defaultProjectView).toBe('list');

    act(() => {
      result.current.setProjectSortBy('name');
    });

    expect(result.current.projectSortBy).toBe('name');

    act(() => {
      result.current.setShowArchivedProjects(true);
    });

    expect(result.current.showArchivedProjects).toBe(true);
  });
});

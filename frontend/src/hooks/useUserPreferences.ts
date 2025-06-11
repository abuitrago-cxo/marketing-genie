import { useState, useEffect, useCallback } from 'react';

export interface UserPreferences {
  // Tema y apariencia
  theme: 'light' | 'dark' | 'system';
  colorScheme: 'original' | 'enhanced' | 'custom';
  
  // Configuración de UI
  sidebarCollapsed: boolean;
  compactMode: boolean;
  animationsEnabled: boolean;
  
  // Configuración de análisis
  defaultAnalysisType: 'codebase' | 'documentation' | 'tasks' | 'research' | 'qa' | 'orchestration';
  autoSaveResults: boolean;
  showAdvancedOptions: boolean;
  
  // Configuración de proyectos
  defaultProjectView: 'grid' | 'list';
  projectSortBy: 'name' | 'updated' | 'created' | 'status';
  showArchivedProjects: boolean;
  
  // Configuración de notificaciones
  enableNotifications: boolean;
  notificationTypes: string[];
  
  // Configuración personalizada
  customSettings: Record<string, any>;
}

const defaultPreferences: UserPreferences = {
  theme: 'system',
  colorScheme: 'original',
  sidebarCollapsed: false,
  compactMode: false,
  animationsEnabled: true,
  defaultAnalysisType: 'codebase',
  autoSaveResults: true,
  showAdvancedOptions: false,
  defaultProjectView: 'grid',
  projectSortBy: 'updated',
  showArchivedProjects: false,
  enableNotifications: true,
  notificationTypes: ['analysis_complete', 'error_alerts', 'system_updates'],
  customSettings: {}
};

const STORAGE_KEY = 'userPreferences';

interface UseUserPreferencesReturn {
  preferences: UserPreferences;
  updatePreference: <K extends keyof UserPreferences>(key: K, value: UserPreferences[K]) => void;
  resetPreferences: () => void;
  exportPreferences: () => string;
  importPreferences: (data: string) => boolean;
  loading: boolean;
  error: string | null;
}

export const useUserPreferences = (): UseUserPreferencesReturn => {
  const [preferences, setPreferences] = useState<UserPreferences>(defaultPreferences);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load preferences from localStorage on mount
  useEffect(() => {
    try {
      setLoading(true);
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Merge with defaults to ensure all properties exist
        const merged = { ...defaultPreferences, ...parsed };
        setPreferences(merged);
      }
    } catch (err) {
      console.error('Error loading user preferences:', err);
      setError('Failed to load preferences');
    } finally {
      setLoading(false);
    }
  }, []);

  // Save preferences to localStorage whenever they change
  useEffect(() => {
    if (!loading) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
        setError(null);
      } catch (err) {
        console.error('Error saving user preferences:', err);
        setError('Failed to save preferences');
      }
    }
  }, [preferences, loading]);

  const updatePreference = useCallback(<K extends keyof UserPreferences>(
    key: K, 
    value: UserPreferences[K]
  ) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value
    }));
  }, []);

  const resetPreferences = useCallback(() => {
    setPreferences(defaultPreferences);
    try {
      localStorage.removeItem(STORAGE_KEY);
      setError(null);
    } catch (err) {
      console.error('Error resetting preferences:', err);
      setError('Failed to reset preferences');
    }
  }, []);

  const exportPreferences = useCallback(() => {
    try {
      return JSON.stringify(preferences, null, 2);
    } catch (err) {
      console.error('Error exporting preferences:', err);
      return '';
    }
  }, [preferences]);

  const importPreferences = useCallback((data: string): boolean => {
    try {
      const parsed = JSON.parse(data);
      // Validate that it's a valid preferences object
      if (typeof parsed === 'object' && parsed !== null) {
        const merged = { ...defaultPreferences, ...parsed };
        setPreferences(merged);
        setError(null);
        return true;
      }
      return false;
    } catch (err) {
      console.error('Error importing preferences:', err);
      setError('Invalid preferences data');
      return false;
    }
  }, []);

  return {
    preferences,
    updatePreference,
    resetPreferences,
    exportPreferences,
    importPreferences,
    loading,
    error
  };
};

// Hook for theme management
export const useTheme = () => {
  const { preferences, updatePreference } = useUserPreferences();

  const setTheme = useCallback((theme: UserPreferences['theme']) => {
    updatePreference('theme', theme);
    
    // Apply theme to document
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else if (theme === 'light') {
      root.classList.remove('dark');
    } else {
      // System theme
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (prefersDark) {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
    }
  }, [updatePreference]);

  // Apply theme on mount and when preferences change
  useEffect(() => {
    setTheme(preferences.theme);
  }, [preferences.theme, setTheme]);

  return {
    theme: preferences.theme,
    setTheme,
    colorScheme: preferences.colorScheme,
    setColorScheme: (scheme: UserPreferences['colorScheme']) => 
      updatePreference('colorScheme', scheme)
  };
};

// Hook for UI preferences
export const useUIPreferences = () => {
  const { preferences, updatePreference } = useUserPreferences();

  return {
    sidebarCollapsed: preferences.sidebarCollapsed,
    setSidebarCollapsed: (collapsed: boolean) => 
      updatePreference('sidebarCollapsed', collapsed),
    
    compactMode: preferences.compactMode,
    setCompactMode: (compact: boolean) => 
      updatePreference('compactMode', compact),
    
    animationsEnabled: preferences.animationsEnabled,
    setAnimationsEnabled: (enabled: boolean) => 
      updatePreference('animationsEnabled', enabled),
  };
};

// Hook for project preferences
export const useProjectPreferences = () => {
  const { preferences, updatePreference } = useUserPreferences();

  return {
    defaultProjectView: preferences.defaultProjectView,
    setDefaultProjectView: (view: UserPreferences['defaultProjectView']) => 
      updatePreference('defaultProjectView', view),
    
    projectSortBy: preferences.projectSortBy,
    setProjectSortBy: (sortBy: UserPreferences['projectSortBy']) => 
      updatePreference('projectSortBy', sortBy),
    
    showArchivedProjects: preferences.showArchivedProjects,
    setShowArchivedProjects: (show: boolean) => 
      updatePreference('showArchivedProjects', show),
  };
};

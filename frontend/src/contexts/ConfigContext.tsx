// frontend/src/contexts/ConfigContext.tsx
import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';

const LOCAL_STORAGE_KEY = 'llmConfig';

export interface LLMConfig {
  llmProvider: "gemini" | "ollama" | "lmstudio" | "";
  geminiApiKey: string;
  ollamaBaseUrl: string;
  ollamaModelName: string;
  lmstudioBaseUrl: string;
  lmstudioModelName: string;
  isLoaded: boolean; // To track if settings have been loaded from local storage/backend
}

export interface ConfigContextType {
  llmConfig: LLMConfig;
  updateConfig: (newConfig: Partial<LLMConfig>) => void;
  saveConfig: () => void; // Explicitly expose save if needed, though updateConfig handles it
  resetToDefaults: () => Promise<void>;
  isLoading: boolean; // Expose a loading state for initial load
}

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

interface ConfigProviderProps {
  children: ReactNode;
}

// Define initial/empty state structure
const initialConfigState: LLMConfig = {
  llmProvider: "",
  geminiApiKey: "",
  ollamaBaseUrl: "",
  ollamaModelName: "",
  lmstudioBaseUrl: "",
  lmstudioModelName: "",
  isLoaded: false,
};

export const ConfigProvider: React.FC<ConfigProviderProps> = ({ children }) => {
  const [llmConfig, setLlmConfig] = useState<LLMConfig>(initialConfigState);
  const [isLoading, setIsLoading] = useState<boolean>(true); // For initial load from backend/localStorage

  const saveConfigToLocalStorage = useCallback((configToSave: LLMConfig) => {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(configToSave));
  }, []);

  const fetchAndSetDefaults = useCallback(async (isInitialLoad = false) => {
    if (!isInitialLoad) setIsLoading(true);
    try {
      const response = await fetch('/agent/config-defaults');
      if (!response.ok) {
        throw new Error(`Failed to fetch default config: ${response.statusText}`);
      }
      const defaults: Partial<LLMConfig> = await response.json();

      // Ensure isLoaded is not part of what we get from backend, set it manually
      const newConfig: LLMConfig = {
        ...initialConfigState, // Start with a clean slate of known fields
        llmProvider: defaults.llmProvider || "gemini", // Ensure provider has a fallback
        geminiApiKey: defaults.geminiApiKey || "",
        ollamaBaseUrl: defaults.ollamaBaseUrl || "",
        ollamaModelName: defaults.ollamaModelName || "",
        lmstudioBaseUrl: defaults.lmstudioBaseUrl || "",
        lmstudioModelName: defaults.lmstudioModelName || "",
        isLoaded: true,
      };
      setLlmConfig(newConfig);
      saveConfigToLocalStorage(newConfig); // Save fetched defaults as the new baseline
      console.log("Fetched and applied default configurations:", newConfig);
    } catch (error) {
      console.error("Error fetching default configurations:", error);
      // In case of error, ensure we still have a valid state and mark as loaded
      setLlmConfig(prevConfig => ({ ...prevConfig, isLoaded: true }));
    } finally {
      setIsLoading(false);
    }
  }, [saveConfigToLocalStorage]);

  useEffect(() => {
    const loadStoredConfig = () => {
      const storedConfigJson = localStorage.getItem(LOCAL_STORAGE_KEY);
      if (storedConfigJson) {
        try {
          const storedConfig: LLMConfig = JSON.parse(storedConfigJson);
          // Ensure all keys are present, even if old config was stored
           const validatedConfig: LLMConfig = {
            ...initialConfigState,
            ...storedConfig,
            isLoaded: true, // Mark as loaded from local storage
          };
          setLlmConfig(validatedConfig);
          setIsLoading(false);
          console.log("Loaded configuration from local storage:", validatedConfig);
        } catch (e) {
          console.error("Error parsing stored LLM config, fetching defaults.", e);
          localStorage.removeItem(LOCAL_STORAGE_KEY); // Clear corrupted data
          fetchAndSetDefaults(true);
        }
      } else {
        console.log("No configuration found in local storage, fetching defaults.");
        fetchAndSetDefaults(true);
      }
    };
    loadStoredConfig();
  }, [fetchAndSetDefaults]);

  const updateConfig = useCallback((newConfig: Partial<LLMConfig>) => {
    setLlmConfig(prevConfig => {
      const updated = { ...prevConfig, ...newConfig, isLoaded: true };
      saveConfigToLocalStorage(updated);
      return updated;
    });
  }, [saveConfigToLocalStorage]);

  const saveConfig = useCallback(() => {
    saveConfigToLocalStorage(llmConfig);
  }, [llmConfig, saveConfigToLocalStorage]);

  const resetToDefaults = useCallback(async () => {
    console.log("Resetting configuration to backend defaults.");
    // Clear local storage first to ensure fresh fetch is not overridden by stale useEffect load
    localStorage.removeItem(LOCAL_STORAGE_KEY);
    await fetchAndSetDefaults();
  }, [fetchAndSetDefaults]);


  return (
    <ConfigContext.Provider value={{ llmConfig, updateConfig, saveConfig, resetToDefaults, isLoading }}>
      {children}
    </ConfigContext.Provider>
  );
};

export const useConfig = (): ConfigContextType => {
  const context = useContext(ConfigContext);
  if (context === undefined) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  return context;
};

import React, { createContext, useContext, useEffect, useState } from 'react';
import { Auth0Provider as Auth0ProviderBase, useAuth0 } from '@auth0/auth0-react';

// Auth0 configuration
const getEnv = (viteKey: string, craKey: string): string => {
  // Vite
  if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env[viteKey]) {
    return import.meta.env[viteKey] as string;
  }
  // CRA/Node
  if (typeof process !== 'undefined' && process.env && process.env[craKey]) {
    return process.env[craKey] as string;
  }
  return '';
};

const auth0Config = {
  domain: getEnv('VITE_AUTH0_DOMAIN', 'REACT_APP_AUTH0_DOMAIN'),
  clientId: getEnv('VITE_AUTH0_CLIENT_ID', 'REACT_APP_AUTH0_CLIENT_ID'),
  authorizationParams: {
    redirect_uri: window.location.origin,
    audience: getEnv('VITE_AUTH0_AUDIENCE', 'REACT_APP_AUTH0_AUDIENCE'),
    scope: 'openid profile email'
  }
};

// Auth context type
interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: any;
  loginWithRedirect: () => void;
  logout: () => void;
  getAccessTokenSilently: () => Promise<string>;
  githubConnected: boolean;
  checkGitHubConnection: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth0 Provider wrapper
export const Auth0Provider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <Auth0ProviderBase {...auth0Config}>
      <AuthContextProvider>
        {children}
      </AuthContextProvider>
    </Auth0ProviderBase>
  );
};

// Auth context provider
const AuthContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const {
    isAuthenticated,
    isLoading,
    user,
    loginWithRedirect,
    logout: auth0Logout,
    getAccessTokenSilently
  } = useAuth0();

  const [githubConnected, setGithubConnected] = useState(false);

  const logout = () => {
    auth0Logout({
      logoutParams: {
        returnTo: window.location.origin
      }
    });
  };

  const checkGitHubConnection = async () => {
    if (!isAuthenticated) {
      setGithubConnected(false);
      return;
    }

    try {
      const token = await getAccessTokenSilently();
      const response = await fetch('/api/v1/github/connection/status', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setGithubConnected(data.connected);
      } else {
        setGithubConnected(false);
      }
    } catch (error) {
      console.error('Failed to check GitHub connection:', error);
      setGithubConnected(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      checkGitHubConnection();
    }
  }, [isAuthenticated, isLoading]);

  const value: AuthContextType = {
    isAuthenticated,
    isLoading,
    user,
    loginWithRedirect,
    logout,
    getAccessTokenSilently,
    githubConnected,
    checkGitHubConnection
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an Auth0Provider');
  }
  return context;
};

// Login button component
export const LoginButton: React.FC = () => {
  const { loginWithRedirect, isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return null;
  }

  return (
    <button
      onClick={() => loginWithRedirect()}
      className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
    >
      Log In
    </button>
  );
};

// Logout button component
export const LogoutButton: React.FC = () => {
  const { logout, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return null;
  }

  return (
    <button
      onClick={() => logout()}
      className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
    >
      Log Out
    </button>
  );
};

// User profile component
export const UserProfile: React.FC = () => {
  const { user, isAuthenticated, githubConnected } = useAuth();

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="flex items-center space-x-3">
      {user.picture && (
        <img
          src={user.picture}
          alt={user.name}
          className="w-8 h-8 rounded-full"
        />
      )}
      <div className="flex flex-col">
        <span className="text-sm font-medium text-gray-900 dark:text-white">
          {user.name}
        </span>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {user.email}
          </span>
          {githubConnected && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
              GitHub Connected
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

// Protected route component
export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Authentication Required
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Please log in to access this application.
          </p>
          <LoginButton />
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

// GitHub connection status component
export const GitHubConnectionStatus: React.FC = () => {
  const { githubConnected, checkGitHubConnection, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return null;
  }

  const handleConnectGitHub = () => {
    // Redirect to Auth0 with GitHub connection
    const auth0Domain = process.env.REACT_APP_AUTH0_DOMAIN;
    const clientId = process.env.REACT_APP_AUTH0_CLIENT_ID;
    const redirectUri = encodeURIComponent(window.location.origin);
    
    const githubConnectionUrl = `https://${auth0Domain}/authorize?` +
      `response_type=code&` +
      `client_id=${clientId}&` +
      `redirect_uri=${redirectUri}&` +
      `scope=openid profile email&` +
      `connection=github`;
    
    window.location.href = githubConnectionUrl;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0">
            <svg className="w-6 h-6 text-gray-900 dark:text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clipRule="evenodd" />
            </svg>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-900 dark:text-white">
              GitHub Integration
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {githubConnected ? 'Connected and ready to import repositories' : 'Connect to import and analyze your repositories'}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {githubConnected ? (
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                Connected
              </span>
              <button
                onClick={checkGitHubConnection}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                title="Refresh connection status"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            </div>
          ) : (
            <button
              onClick={handleConnectGitHub}
              className="bg-gray-900 hover:bg-gray-800 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Connect GitHub
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

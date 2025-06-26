import { useState, useEffect, useCallback } from 'react';
import { MCPServerPackage, MCPServerPackageStatus } from '@/types/mcp'; // Assuming types are moved to a central place
import { getApiBaseUrl } from '../config/api';

// Backend response type (simplified for now, expand as needed)
interface MCPServerResponse {
  id: number;
  name: string; // This is the unique identifier like '@modelcontextprotocol/server-filesystem'
  base_url: string; // Can be repo URL or main URL
  description: string | null;
  enabled: boolean;
  installation_status: string | null; // e.g., "pending", "installing", "installed", "failed"
  available_tools_json: Record<string, any> | null;
  created_at: string;
  updated_at: string;
  // Fields from MCPServerInstallRequest that might be relevant if returned or stored
  source_type?: string; 
}

interface MCPServerInstallRequest {
  name: string;
  source_url: string; 
  source_type: string; // "github" | "npm" | "local" | "url"
  description?: string;
  auto_enable?: boolean;
}

const API_BASE_URL = getApiBaseUrl(); // Adjust if your API prefix is different

// Helper to transform backend response to frontend package type
const transformBackendPackage = (pkg: MCPServerResponse): MCPServerPackage => {
  // Basic mapping
  const fePackage: MCPServerPackage = {
    id: pkg.id.toString(), // Convert number id to string for frontend consistency
    name: pkg.name, 
    displayName: pkg.name.split('/').pop()?.replace(/-/g, ' ').replace(/^server /i, '').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') || pkg.name,
    description: pkg.description || 'No description available.',
    author: pkg.name.startsWith('@') ? pkg.name.split('/')[0].substring(1) : 'Unknown',
    version: '0.0.0', // Placeholder - not directly available
    repository: pkg.source_type === 'github' ? pkg.base_url : undefined, // Assuming base_url is repo if github
    homepage: pkg.source_type !== 'github' ? pkg.base_url : undefined,
    keywords: [], // Placeholder
    category: 'General', // Placeholder
    downloads: 0, // Placeholder
    stars: 0, // Placeholder
    lastUpdated: new Date(pkg.updated_at).toISOString(),
    sourceType: (pkg.source_type as 'github' | 'npm' | 'pypi' | 'custom') || 'custom', // Cast and default
    sourceUrl: pkg.base_url, // Or a specific source_url if available from install details
    capabilities: pkg.available_tools_json ? Object.keys(pkg.available_tools_json) : [],
    status: (pkg.installation_status?.toLowerCase() as MCPServerPackageStatus) || (pkg.enabled ? 'available' : 'disabled'),
    // requirements: {} // Placeholder
  };

  // Refine status based on enabled flag if installation_status is 'installed'
  if (fePackage.status === 'installed' && !pkg.enabled) {
    fePackage.status = 'disabled';
  }
  if (pkg.installation_status === 'PENDING' || pkg.installation_status === 'INSTALLING') {
    fePackage.status = pkg.installation_status.toLowerCase() as MCPServerPackageStatus;
  }
  if (pkg.installation_status === 'FAILED') {
    fePackage.status = 'failed';
  }
  
  return fePackage;
};

export const useMCPMarketplace = (pollingIntervalMs: number = 5000) => {
  const [packages, setPackages] = useState<MCPServerPackage[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPackages = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/servers/?enabled_only=false&limit=100`); // Fetch all, including disabled
      if (!response.ok) {
        throw new Error(`Failed to fetch MCP packages: ${response.statusText}`);
      }
      const data: MCPServerResponse[] = await response.json();
      setPackages(data.map(transformBackendPackage));
    } catch (e: any) {
      setError(e.message);
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPackages();
  }, [fetchPackages]);

  // Effect for polling packages with 'installing' or 'pending' status
  useEffect(() => {
    const packagesToPoll = packages.filter(
      (p) => p.status === 'installing' || p.status === 'pending'
    );

    if (packagesToPoll.length > 0) {
      const intervalId = setInterval(() => {
        console.log('Polling for MCP package status updates...');
        fetchPackages();
      }, pollingIntervalMs);
      return () => clearInterval(intervalId);
    }
  }, [packages, fetchPackages, pollingIntervalMs]);

  const installPackage = useCallback(async (installData: MCPServerInstallRequest): Promise<MCPServerPackage | null> => {
    // Optimistically update UI or wait for backend to confirm?
    // For now, we'll call the API and then re-fetch the list to get updated statuses.
    try {
      const response = await fetch(`${API_BASE_URL}/servers/install`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(installData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Installation request failed with status: ' + response.statusText }));
        throw new Error(errorData.detail || `Failed to install MCP package: ${response.statusText}`);
      }
      
      const newServerResponse: MCPServerResponse = await response.json();
      
      // After install request, refetch packages to get PENDING/INSTALLING status
      // The actual installation is a background task on the server.
      fetchPackages(); 
      return transformBackendPackage(newServerResponse); // Return the initially created/pending server record

    } catch (e: any) {
      setError(e.message);
      console.error('Installation error:', e);
      return null;
    }
  }, [fetchPackages]);

  return { packages, loading, error, fetchPackages, installPackage };
};

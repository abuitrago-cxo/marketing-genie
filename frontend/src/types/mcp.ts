// Centralized types for MCP Marketplace

export type MCPServerPackageStatus = 'available' | 'installing' | 'installed' | 'failed' | 'disabled' | 'pending' | 'uninstalling';

export interface MCPServerPackage {
  id: string;
  name: string; // e.g., @modelcontextprotocol/server-filesystem
  displayName: string; // e.g., File System
  description: string;
  author: string;
  version: string;
  repository?: string;
  homepage?: string;
  keywords: string[];
  category: string;
  downloads: number;
  stars: number;
  lastUpdated: string; // ISO date string
  sourceType: 'github' | 'npm' | 'pypi' | 'custom' | 'local' | 'url'; // Added local and url from backend
  sourceUrl: string;
  installCommand?: string; // May not be needed if all installs are via API
  documentation?: string;
  examples?: string[];
  capabilities: string[];
  requirements?: {
    node?: string;
    python?: string;
    system?: string[];
  };
  status: MCPServerPackageStatus;
}

// This can be used by the MCPMarketplace component for the install function prop if needed
// or directly by the hook for the install request body.
export interface MCPServerInstallPayload {
  name: string; // The unique name for the server, e.g., "my-custom-filesystem"
  source_url: string; // e.g., git repo URL, npm package URL
  source_type: 'github' | 'npm' | 'local' | 'url';
  description?: string;
  auto_enable?: boolean;
  // Potentially auth_config if needed for private repos/packages
}

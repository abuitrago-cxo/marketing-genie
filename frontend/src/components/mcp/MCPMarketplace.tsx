import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Search, 
  Download, 
  Star, 
  GitBranch, 
  Calendar,
  Package,
  FileText,
  Globe,
  Loader2,
  CheckCircle,
  AlertCircle,
  Settings2, // For capabilities
  Info,      // For generic info
  RefreshCw, // For retry
  ServerCrash, // For error display
  XCircle // For unsupported install
} from 'lucide-react';
import { MCPServerPackage, MCPServerPackageStatus, MCPServerInstallPayload } from '@/types/mcp';
import { useMCPMarketplace } from '@/hooks/useMCPMarketplace';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

// Props for the component - simplified as hook manages most state
interface MCPMarketplaceProps {}

const MCPMarketplace: React.FC<MCPMarketplaceProps> = () => {
  const { 
    packages: fetchedPackages,
    loading,
    error,
    fetchPackages,
    installPackage 
  } = useMCPMarketplace();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [sortBy, setSortBy] = useState('Name'); // Default sort

  // Derive categories from fetched packages
  const categories = useMemo(() => {
    const allCategories = new Set<string>(['All']);
    fetchedPackages.forEach(pkg => allCategories.add(pkg.category));
    return Array.from(allCategories);
  }, [fetchedPackages]);

  // Filter and sort packages
  const filteredPackages = useMemo(() => {
    return fetchedPackages
      .filter(pkg => 
        (pkg.displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
         pkg.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
         pkg.name.toLowerCase().includes(searchQuery.toLowerCase())) &&
        (selectedCategory === 'All' || pkg.category === selectedCategory)
      )
      .sort((a, b) => {
        switch (sortBy) {
          case 'Most Installs': // Placeholder, as we don't have real install counts
            return (b.downloads || 0) - (a.downloads || 0);
          case 'Newest':
            return new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime();
          case 'GitHub Stars': // Placeholder
            return (b.stars || 0) - (a.stars || 0);
          case 'Name':
          default:
            return a.displayName.localeCompare(b.displayName);
        }
      });
  }, [fetchedPackages, searchQuery, selectedCategory, sortBy]);

  const handleInstall = async (pkg: MCPServerPackage) => {
    // Define source types supported by the backend's install endpoint
    const supportedInstallSourceTypes: Array<MCPServerInstallPayload['source_type']> = ['github', 'npm', 'local', 'url'];

    if (!supportedInstallSourceTypes.includes(pkg.sourceType as MCPServerInstallPayload['source_type'])) {
      console.warn(`Installation for sourceType '${pkg.sourceType}' is not directly supported for package ${pkg.name}.`);
      // Optionally: use a toast notification to inform the user
      return; 
    }

    const installPayload: MCPServerInstallPayload = {
      name: pkg.name, 
      source_url: pkg.sourceUrl,
      source_type: pkg.sourceType as MCPServerInstallPayload['source_type'], 
      description: pkg.description,
      auto_enable: true, 
    };
    try {
      await installPackage(installPayload);
    } catch (installError) {
      console.error("Installation trigger failed in component:", installError);
    }
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const getStatusIcon = (status: MCPServerPackageStatus) => {
    switch (status) {
      case 'installed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'installing':
      case 'pending':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'available':
        return <Package className="w-4 h-4 text-gray-500" />;
      case 'disabled':
        return <Info className="w-4 h-4 text-yellow-500" />;
      default:
        return <Package className="w-4 h-4 text-gray-400" />;
    }
  };
  
  const getStatusTooltip = (status: MCPServerPackageStatus) => {
    switch (status) {
      case 'installed': return 'Installed & Enabled';
      case 'installing': return 'Installation in progress...';
      case 'pending': return 'Installation pending...';
      case 'failed': return 'Installation failed';
      case 'available': return 'Available for installation';
      case 'disabled': return 'Installed but disabled';
      default: return 'Unknown status';
    }
  };

  const PackageCard: React.FC<{ pkg: MCPServerPackage }> = ({ pkg }) => {
    const isInstallingOrPending = pkg.status === 'installing' || pkg.status === 'pending';
    const isInstalled = pkg.status === 'installed';
    const isDisabledStatus = pkg.status === 'disabled';
    const isFailed = pkg.status === 'failed';

    const supportedInstallSourceTypes: Array<MCPServerInstallPayload['source_type']> = ['github', 'npm', 'local', 'url'];
    const isUnsupportedSourceType = !supportedInstallSourceTypes.includes(pkg.sourceType as MCPServerInstallPayload['source_type']);

    let installButtonTooltipMessage = 'Install Package';
    if (isUnsupportedSourceType) {
      installButtonTooltipMessage = `Installation via source type '${pkg.sourceType}' is not directly supported.`;
    } else if (isInstallingOrPending) {
      installButtonTooltipMessage = pkg.status === 'installing' ? 'Installation in progress...' : 'Installation pending...';
    } else if (isInstalled) {
      installButtonTooltipMessage = 'Package is already installed and enabled.';
    } else if (isDisabledStatus) {
      installButtonTooltipMessage = 'Package is installed but currently disabled. Check settings to enable.';
    } else if (isFailed) {
      installButtonTooltipMessage = 'Previous installation attempt failed. Click to retry.';
    }

    return (
      <Card className="flex flex-col justify-between h-full">
        <CardHeader>
          <div className="flex justify-between items-start">
            <CardTitle className="text-lg">{pkg.displayName}</CardTitle>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="cursor-help">{getStatusIcon(pkg.status)}</div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{getStatusTooltip(pkg.status)}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <CardDescription className="text-xs text-gray-500 truncate" title={pkg.name}>{pkg.name}</CardDescription>
          <CardDescription className="h-16 overflow-y-auto text-sm">{pkg.description}</CardDescription>
        </CardHeader>
        <CardContent className="flex-grow flex flex-col justify-between">
          <div className="space-y-2 mb-4 text-xs">
            {pkg.author && <div className="flex items-center"><Info className="w-3 h-3 mr-1.5 text-gray-400" /> Author: {pkg.author}</div>}
            {pkg.version && <div className="flex items-center"><GitBranch className="w-3 h-3 mr-1.5 text-gray-400" /> Version: {pkg.version}</div>}
            <div className="flex items-center"><Calendar className="w-3 h-3 mr-1.5 text-gray-400" /> Updated: {new Date(pkg.lastUpdated).toLocaleDateString()}</div>
            {pkg.capabilities.length > 0 && (
              <div className="flex items-start">
                <Settings2 className="w-3 h-3 mr-1.5 text-gray-400 mt-0.5" />
                <div>
                  Capabilities:
                  <div className="flex flex-wrap gap-1 mt-1">
                    {pkg.capabilities.slice(0, 3).map(cap => <Badge key={cap} variant="secondary" className="text-xs">{cap}</Badge>)}
                    {pkg.capabilities.length > 3 && <Badge variant="outline">+{pkg.capabilities.length - 3} more</Badge>}
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="flex space-x-2">
            <TooltipProvider>
              <Tooltip delayDuration={100}>
                <TooltipTrigger asChild>
                  {/* Span needed for tooltip on disabled button */}
                  <span tabIndex={0} className="flex-1">
                    <Button
                      size="sm"
                      onClick={() => handleInstall(pkg)} // handleInstall itself checks for support
                      disabled={isInstalled || isInstallingOrPending || isDisabledStatus || isUnsupportedSourceType}
                      className="w-full"
                      aria-label={installButtonTooltipMessage}
                    >
                      {isInstallingOrPending ? (
                        <><Loader2 className="w-4 h-4 mr-1 animate-spin" /> {pkg.status === 'installing' ? 'Installing...' : 'Pending...'}</>
                      ) : isInstalled ? (
                        <><CheckCircle className="w-4 h-4 mr-1" /> Installed</>
                      ) : isDisabledStatus ? (
                        <><Info className="w-4 h-4 mr-1" /> Disabled</>
                      ) : isFailed ? (
                        <><Download className="w-4 h-4 mr-1" /> Retry Install</>
                      ) : isUnsupportedSourceType ? (
                        <><XCircle className="w-4 h-4 mr-1 text-orange-500"/> Install</> 
                      ) : (
                        <><Download className="w-4 h-4 mr-1" /> Install</>
                      )}
                    </Button>
                  </span>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{installButtonTooltipMessage}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            
            {pkg.repository && (
              <TooltipProvider>
                <Tooltip delayDuration={100}>
                  <TooltipTrigger asChild>
                    <Button variant="outline" size="sm" asChild>
                      <a href={pkg.repository} target="_blank" rel="noopener noreferrer" aria-label="View Repository on GitHub">
                        <GitBranch className="w-4 h-4" />
                      </a>
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent><p>View Repository</p></TooltipContent>
                </Tooltip>
              </TooltipProvider>
            )}
            
            {pkg.homepage && (
              <TooltipProvider>
                <Tooltip delayDuration={100}>
                  <TooltipTrigger asChild>
                    <Button variant="outline" size="sm" asChild>
                      <a href={pkg.homepage} target="_blank" rel="noopener noreferrer" aria-label="View Homepage">
                        <Globe className="w-4 h-4" />
                      </a>
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent><p>View Homepage</p></TooltipContent>
                </Tooltip>
              </TooltipProvider>
            )}
          </div>
        </CardContent>
      </Card>
    );
  };

  if (loading && fetchedPackages.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="w-12 h-12 animate-spin text-primary" />
        <p className="ml-4 text-lg">Loading MCP Marketplace...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-red-500">
        <CardHeader>
          <CardTitle className="flex items-center text-red-600">
            <ServerCrash className="w-6 h-6 mr-2" /> Error Loading Marketplace
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-500 mb-4">{error}</p>
          <Button onClick={() => fetchPackages()} >
            <RefreshCw className="w-4 h-4 mr-2" /> Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6 p-1">
      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder={`Search ${fetchedPackages.length} MCP servers...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Select category" />
          </SelectTrigger>
          <SelectContent>
            {categories.map(category => (
              <SelectItem key={category} value={category}>
                {category}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={sortBy} onValueChange={setSortBy}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Name">Name</SelectItem>
            {/* <SelectItem value="Most Installs">Most Installs</SelectItem> */}
            <SelectItem value="Newest">Newest</SelectItem>
            {/* <SelectItem value="GitHub Stars">GitHub Stars</SelectItem> */}
          </SelectContent>
        </Select>
      </div>

      {/* Results */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">
            {filteredPackages.length} server{filteredPackages.length !== 1 ? 's' : ''} found
          </h3>
          {loading && <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />}
        </div>

        {filteredPackages.length === 0 && !loading ? (
          <Card className="text-center py-8">
            <CardContent>
              <Package className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold mb-2">No servers found</h3>
              <p className="text-muted-foreground">
                Try adjusting your search criteria or check back later.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredPackages.map(pkg => (
              <PackageCard key={pkg.id} pkg={pkg} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MCPMarketplace;

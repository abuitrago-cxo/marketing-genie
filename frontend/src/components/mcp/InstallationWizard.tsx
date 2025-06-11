import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  ChevronLeft,
  ChevronRight,
  Package,
  Download,
  Settings,
  CheckCircle,
  AlertCircle,
  Loader2,
  Github,
  Globe,
  Terminal
} from 'lucide-react';

interface InstallationStep {
  id: string;
  title: string;
  description: string;
  component: React.ReactNode;
}

interface InstallationWizardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  packageInfo?: any;
  onComplete: (serverConfig: any) => Promise<void>;
}

const InstallationWizard: React.FC<InstallationWizardProps> = ({
  open,
  onOpenChange,
  packageInfo,
  onComplete
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [installing, setInstalling] = useState(false);
  const [installationProgress, setInstallationProgress] = useState(0);
  const [installationStatus, setInstallationStatus] = useState<'idle' | 'installing' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const [formData, setFormData] = useState({
    source_type: 'github',
    source_url: '',
    name: '',
    description: '',
    install_location: 'local',
    auto_start: true,
    auth_config: {
      auth_type: 'none',
      api_key: '',
      bearer_token: '',
      username: '',
      password: ''
    }
  });

  React.useEffect(() => {
    if (packageInfo) {
      setFormData(prev => ({
        ...prev,
        source_type: packageInfo.sourceType || 'github',
        source_url: packageInfo.sourceUrl || packageInfo.repository || '',
        name: packageInfo.displayName || packageInfo.name || '',
        description: packageInfo.description || ''
      }));
    }
  }, [packageInfo]);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const simulateInstallation = async () => {
    setInstalling(true);
    setInstallationStatus('installing');
    setInstallationProgress(0);

    // Simulate installation steps
    const steps = [
      { message: 'Downloading package...', progress: 20 },
      { message: 'Installing dependencies...', progress: 40 },
      { message: 'Configuring server...', progress: 60 },
      { message: 'Starting server...', progress: 80 },
      { message: 'Verifying installation...', progress: 100 }
    ];

    for (const step of steps) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setInstallationProgress(step.progress);
    }

    // Simulate success or failure
    const success = Math.random() > 0.2; // 80% success rate
    
    if (success) {
      setInstallationStatus('success');
      setTimeout(() => {
        onComplete(formData);
        onOpenChange(false);
      }, 1500);
    } else {
      setInstallationStatus('error');
      setErrorMessage('Installation failed: Unable to start server. Please check your configuration.');
    }
    
    setInstalling(false);
  };

  const steps: InstallationStep[] = [
    {
      id: 'source',
      title: 'Source Configuration',
      description: 'Configure the source and installation details',
      component: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="source_type">Source Type</Label>
            <Select 
              value={formData.source_type} 
              onValueChange={(value) => handleInputChange('source_type', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="github">
                  <div className="flex items-center">
                    <Github className="w-4 h-4 mr-2" />
                    GitHub Repository
                  </div>
                </SelectItem>
                <SelectItem value="npm">
                  <div className="flex items-center">
                    <Package className="w-4 h-4 mr-2" />
                    NPM Package
                  </div>
                </SelectItem>
                <SelectItem value="url">
                  <div className="flex items-center">
                    <Globe className="w-4 h-4 mr-2" />
                    Direct URL
                  </div>
                </SelectItem>
                <SelectItem value="local">
                  <div className="flex items-center">
                    <Terminal className="w-4 h-4 mr-2" />
                    Local Path
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="source_url">Source URL/Path</Label>
            <Input
              id="source_url"
              value={formData.source_url}
              onChange={(e) => handleInputChange('source_url', e.target.value)}
              placeholder={
                formData.source_type === 'github' ? 'https://github.com/user/repo' :
                formData.source_type === 'npm' ? '@scope/package-name' :
                formData.source_type === 'url' ? 'https://example.com/server.zip' :
                '/path/to/local/server'
              }
            />
          </div>

          <div>
            <Label htmlFor="name">Server Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="My MCP Server"
            />
          </div>

          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder="Describe what this server provides..."
              rows={3}
            />
          </div>
        </div>
      )
    },
    {
      id: 'configuration',
      title: 'Server Configuration',
      description: 'Configure server settings and authentication',
      component: (
        <div className="space-y-4">
          <div>
            <Label htmlFor="install_location">Installation Location</Label>
            <Select 
              value={formData.install_location} 
              onValueChange={(value) => handleInputChange('install_location', value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="local">Local Installation</SelectItem>
                <SelectItem value="docker">Docker Container</SelectItem>
                <SelectItem value="remote">Remote Server</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="auto_start"
              checked={formData.auto_start}
              onChange={(e) => handleInputChange('auto_start', e.target.checked)}
              className="rounded"
            />
            <Label htmlFor="auto_start">Auto-start server after installation</Label>
          </div>

          {packageInfo && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Package Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Version:</span>
                  <Badge variant="outline">{packageInfo.version}</Badge>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Author:</span>
                  <span>{packageInfo.author}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Category:</span>
                  <Badge variant="secondary">{packageInfo.category}</Badge>
                </div>
                {packageInfo.requirements && (
                  <div className="text-sm">
                    <span className="font-medium">Requirements:</span>
                    <ul className="list-disc list-inside mt-1 text-muted-foreground">
                      {packageInfo.requirements.node && (
                        <li>Node.js {packageInfo.requirements.node}</li>
                      )}
                      {packageInfo.requirements.python && (
                        <li>Python {packageInfo.requirements.python}</li>
                      )}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      )
    },
    {
      id: 'installation',
      title: 'Installation',
      description: 'Installing and configuring the MCP server',
      component: (
        <div className="space-y-6">
          {installationStatus === 'idle' && (
            <div className="text-center py-8">
              <Package className="w-16 h-16 mx-auto text-blue-500 mb-4" />
              <h3 className="text-lg font-semibold mb-2">Ready to Install</h3>
              <p className="text-muted-foreground mb-4">
                Click "Install" to begin the installation process.
              </p>
              <Button onClick={simulateInstallation} size="lg">
                <Download className="w-4 h-4 mr-2" />
                Install Server
              </Button>
            </div>
          )}

          {installationStatus === 'installing' && (
            <div className="space-y-4">
              <div className="text-center">
                <Loader2 className="w-16 h-16 mx-auto text-blue-500 animate-spin mb-4" />
                <h3 className="text-lg font-semibold mb-2">Installing...</h3>
                <p className="text-muted-foreground">
                  Please wait while we install and configure your MCP server.
                </p>
              </div>
              <Progress value={installationProgress} className="w-full" />
              <p className="text-center text-sm text-muted-foreground">
                {installationProgress}% complete
              </p>
            </div>
          )}

          {installationStatus === 'success' && (
            <div className="text-center py-8">
              <CheckCircle className="w-16 h-16 mx-auto text-green-500 mb-4" />
              <h3 className="text-lg font-semibold mb-2">Installation Complete!</h3>
              <p className="text-muted-foreground">
                Your MCP server has been successfully installed and configured.
              </p>
            </div>
          )}

          {installationStatus === 'error' && (
            <div className="space-y-4">
              <div className="text-center py-8">
                <AlertCircle className="w-16 h-16 mx-auto text-red-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">Installation Failed</h3>
              </div>
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{errorMessage}</AlertDescription>
              </Alert>
              <div className="flex justify-center space-x-2">
                <Button variant="outline" onClick={() => setInstallationStatus('idle')}>
                  Try Again
                </Button>
                <Button variant="outline" onClick={() => onOpenChange(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </div>
      )
    }
  ];

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return formData.source_url && formData.name;
      case 1:
        return true;
      case 2:
        return installationStatus === 'success';
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Install MCP Server</DialogTitle>
          <DialogDescription>
            Follow the steps to install and configure your MCP server.
          </DialogDescription>
        </DialogHeader>

        {/* Progress indicator */}
        <div className="flex items-center justify-between mb-6">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={`
                w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                ${index <= currentStep ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-600'}
              `}>
                {index + 1}
              </div>
              {index < steps.length - 1 && (
                <div className={`
                  w-12 h-0.5 mx-2
                  ${index < currentStep ? 'bg-blue-500' : 'bg-gray-200'}
                `} />
              )}
            </div>
          ))}
        </div>

        {/* Current step content */}
        <div className="min-h-[400px]">
          <div className="mb-4">
            <h3 className="text-lg font-semibold">{steps[currentStep].title}</h3>
            <p className="text-muted-foreground">{steps[currentStep].description}</p>
          </div>
          {steps[currentStep].component}
        </div>

        <DialogFooter>
          <div className="flex justify-between w-full">
            <Button 
              variant="outline" 
              onClick={handlePrevious}
              disabled={currentStep === 0 || installing}
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Previous
            </Button>
            
            <div className="flex space-x-2">
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              
              {currentStep < steps.length - 1 ? (
                <Button 
                  onClick={handleNext}
                  disabled={!canProceed() || installing}
                >
                  Next
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              ) : (
                <Button 
                  onClick={() => onOpenChange(false)}
                  disabled={installationStatus !== 'success'}
                >
                  Finish
                </Button>
              )}
            </div>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default InstallationWizard;

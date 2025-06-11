import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { useUserPreferences, useTheme, useUIPreferences, useProjectPreferences } from '@/hooks/useUserPreferences';
import {
  Settings,
  User,
  Bell,
  Shield,
  Palette,
  Database,
  Bot,
  Save,
  Download,
  Upload,
  RotateCcw,
  Monitor,
  Sun,
  Moon,
  Grid,
  List,
  Eye,
  EyeOff
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const {
    preferences,
    updatePreference,
    resetPreferences,
    exportPreferences,
    importPreferences,
    loading,
    error
  } = useUserPreferences();

  const { theme, setTheme, colorScheme, setColorScheme } = useTheme();
  const {
    sidebarCollapsed,
    setSidebarCollapsed,
    compactMode,
    setCompactMode,
    animationsEnabled,
    setAnimationsEnabled
  } = useUIPreferences();

  const {
    defaultProjectView,
    setDefaultProjectView,
    projectSortBy,
    setProjectSortBy,
    showArchivedProjects,
    setShowArchivedProjects
  } = useProjectPreferences();

  const [importData, setImportData] = useState('');

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Settings className="h-8 w-8 text-gray-600" />
          Settings
        </h1>
        <p className="text-muted-foreground">
          Manage your account, preferences, and system configuration
        </p>
        {error && (
          <div className="mt-2 p-2 bg-red-100 text-red-700 rounded text-sm">
            {error}
          </div>
        )}
        {loading && (
          <div className="mt-2 p-2 bg-blue-100 text-blue-700 rounded text-sm">
            Loading preferences...
          </div>
        )}
      </div>

      {/* Settings tabs */}
      <Tabs defaultValue="appearance" className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="appearance">Appearance</TabsTrigger>
          <TabsTrigger value="ui">Interface</TabsTrigger>
          <TabsTrigger value="projects">Projects</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
        </TabsList>

        <TabsContent value="appearance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Theme & Appearance
              </CardTitle>
              <CardDescription>
                Customize the look and feel of your interface
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-3">
                <Label>Theme</Label>
                <div className="flex gap-2">
                  <Button
                    variant={theme === 'light' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setTheme('light')}
                    className="flex items-center gap-2"
                  >
                    <Sun className="h-4 w-4" />
                    Light
                  </Button>
                  <Button
                    variant={theme === 'dark' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setTheme('dark')}
                    className="flex items-center gap-2"
                  >
                    <Moon className="h-4 w-4" />
                    Dark
                  </Button>
                  <Button
                    variant={theme === 'system' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setTheme('system')}
                    className="flex items-center gap-2"
                  >
                    <Monitor className="h-4 w-4" />
                    System
                  </Button>
                </div>
              </div>

              <div className="space-y-3">
                <Label>Color Scheme</Label>
                <Select value={colorScheme} onValueChange={setColorScheme}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="original">Original (Google Gemini)</SelectItem>
                    <SelectItem value="enhanced">Enhanced</SelectItem>
                    <SelectItem value="custom">Custom</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground">
                  Original preserves the Google Gemini repository styling
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ui" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Monitor className="h-5 w-5" />
                Interface Preferences
              </CardTitle>
              <CardDescription>
                Configure how the interface behaves and appears
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Sidebar Collapsed by Default</Label>
                  <p className="text-sm text-muted-foreground">
                    Start with the sidebar collapsed to save space
                  </p>
                </div>
                <Switch
                  checked={sidebarCollapsed}
                  onCheckedChange={setSidebarCollapsed}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Compact Mode</Label>
                  <p className="text-sm text-muted-foreground">
                    Use smaller spacing and components for more content
                  </p>
                </div>
                <Switch
                  checked={compactMode}
                  onCheckedChange={setCompactMode}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Enable Animations</Label>
                  <p className="text-sm text-muted-foreground">
                    Show smooth transitions and animations
                  </p>
                </div>
                <Switch
                  checked={animationsEnabled}
                  onCheckedChange={setAnimationsEnabled}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="projects" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Project Preferences
              </CardTitle>
              <CardDescription>
                Configure default settings for project management
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-3">
                <Label>Default Project View</Label>
                <div className="flex gap-2">
                  <Button
                    variant={defaultProjectView === 'grid' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setDefaultProjectView('grid')}
                    className="flex items-center gap-2"
                  >
                    <Grid className="h-4 w-4" />
                    Grid
                  </Button>
                  <Button
                    variant={defaultProjectView === 'list' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setDefaultProjectView('list')}
                    className="flex items-center gap-2"
                  >
                    <List className="h-4 w-4" />
                    List
                  </Button>
                </div>
              </div>

              <div className="space-y-3">
                <Label>Default Sort Order</Label>
                <Select value={projectSortBy} onValueChange={setProjectSortBy}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="name">Name</SelectItem>
                    <SelectItem value="updated">Last Updated</SelectItem>
                    <SelectItem value="created">Date Created</SelectItem>
                    <SelectItem value="status">Status</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Show Archived Projects</Label>
                  <p className="text-sm text-muted-foreground">
                    Display archived projects in the project list
                  </p>
                </div>
                <Switch
                  checked={showArchivedProjects}
                  onCheckedChange={setShowArchivedProjects}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                Analysis Preferences
              </CardTitle>
              <CardDescription>
                Configure default settings for AI analysis workflows
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-3">
                <Label>Default Analysis Type</Label>
                <Select
                  value={preferences.defaultAnalysisType}
                  onValueChange={(value) => updatePreference('defaultAnalysisType', value as any)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="codebase">Codebase Analysis</SelectItem>
                    <SelectItem value="documentation">Documentation Analysis</SelectItem>
                    <SelectItem value="tasks">Task Planning</SelectItem>
                    <SelectItem value="research">Research Analysis</SelectItem>
                    <SelectItem value="qa">QA & Testing</SelectItem>
                    <SelectItem value="orchestration">Project Orchestration</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Auto-save Results</Label>
                  <p className="text-sm text-muted-foreground">
                    Automatically save analysis results to project history
                  </p>
                </div>
                <Switch
                  checked={preferences.autoSaveResults}
                  onCheckedChange={(checked) => updatePreference('autoSaveResults', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Show Advanced Options</Label>
                  <p className="text-sm text-muted-foreground">
                    Display advanced configuration options in analysis dialogs
                  </p>
                </div>
                <Switch
                  checked={preferences.showAdvancedOptions}
                  onCheckedChange={(checked) => updatePreference('showAdvancedOptions', checked)}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notification Preferences
              </CardTitle>
              <CardDescription>
                Choose how you want to be notified about important events
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Enable Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive notifications about system events
                  </p>
                </div>
                <Switch
                  checked={preferences.enableNotifications}
                  onCheckedChange={(checked) => updatePreference('enableNotifications', checked)}
                />
              </div>

              {preferences.enableNotifications && (
                <div className="space-y-4 pl-4 border-l-2 border-muted">
                  <div className="space-y-3">
                    <Label>Notification Types</Label>
                    <div className="space-y-2">
                      {[
                        { id: 'analysis_complete', label: 'Analysis Complete', description: 'When AI analysis finishes' },
                        { id: 'error_alerts', label: 'Error Alerts', description: 'When errors occur in workflows' },
                        { id: 'system_updates', label: 'System Updates', description: 'When system updates are available' }
                      ].map((type) => (
                        <div key={type.id} className="flex items-center justify-between">
                          <div className="space-y-0.5">
                            <Label className="text-sm">{type.label}</Label>
                            <p className="text-xs text-muted-foreground">{type.description}</p>
                          </div>
                          <Switch
                            checked={preferences.notificationTypes.includes(type.id)}
                            onCheckedChange={(checked) => {
                              const types = checked
                                ? [...preferences.notificationTypes, type.id]
                                : preferences.notificationTypes.filter(t => t !== type.id);
                              updatePreference('notificationTypes', types);
                            }}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="advanced" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Advanced Settings
              </CardTitle>
              <CardDescription>
                Export, import, and reset your preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div>
                  <Label className="text-base font-medium">Export Preferences</Label>
                  <p className="text-sm text-muted-foreground mb-3">
                    Download your current preferences as a JSON file
                  </p>
                  <Button
                    variant="outline"
                    onClick={() => {
                      const data = exportPreferences();
                      const blob = new Blob([data], { type: 'application/json' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = 'ai-agent-preferences.json';
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                    className="flex items-center gap-2"
                  >
                    <Download className="h-4 w-4" />
                    Export Preferences
                  </Button>
                </div>

                <div>
                  <Label className="text-base font-medium">Import Preferences</Label>
                  <p className="text-sm text-muted-foreground mb-3">
                    Upload a previously exported preferences file
                  </p>
                  <div className="space-y-3">
                    <Textarea
                      placeholder="Paste your preferences JSON here..."
                      value={importData}
                      onChange={(e) => setImportData(e.target.value)}
                      rows={4}
                    />
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        onClick={() => {
                          const input = document.createElement('input');
                          input.type = 'file';
                          input.accept = '.json';
                          input.onchange = (e) => {
                            const file = (e.target as HTMLInputElement).files?.[0];
                            if (file) {
                              const reader = new FileReader();
                              reader.onload = (e) => {
                                const content = e.target?.result as string;
                                setImportData(content);
                              };
                              reader.readAsText(file);
                            }
                          };
                          input.click();
                        }}
                        className="flex items-center gap-2"
                      >
                        <Upload className="h-4 w-4" />
                        Choose File
                      </Button>
                      <Button
                        onClick={() => {
                          if (importPreferences(importData)) {
                            setImportData('');
                            alert('Preferences imported successfully!');
                          } else {
                            alert('Failed to import preferences. Please check the format.');
                          }
                        }}
                        disabled={!importData.trim()}
                        className="flex items-center gap-2"
                      >
                        <Save className="h-4 w-4" />
                        Import
                      </Button>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t">
                  <Label className="text-base font-medium text-red-600">Reset All Preferences</Label>
                  <p className="text-sm text-muted-foreground mb-3">
                    This will reset all preferences to their default values. This action cannot be undone.
                  </p>
                  <Button
                    variant="destructive"
                    onClick={() => {
                      if (confirm('Are you sure you want to reset all preferences? This action cannot be undone.')) {
                        resetPreferences();
                        alert('Preferences have been reset to defaults.');
                      }
                    }}
                    className="flex items-center gap-2"
                  >
                    <RotateCcw className="h-4 w-4" />
                    Reset to Defaults
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Debug Information
              </CardTitle>
              <CardDescription>
                Current preferences state for debugging
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label>Show Debug Info</Label>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      const debugInfo = {
                        preferences,
                        timestamp: new Date().toISOString(),
                        userAgent: navigator.userAgent,
                        localStorage: Object.keys(localStorage).filter(key => key.startsWith('userPreferences'))
                      };
                      console.log('Debug Info:', debugInfo);
                      alert('Debug information logged to console');
                    }}
                  >
                    Log to Console
                  </Button>
                </div>
                <div className="p-3 bg-muted rounded text-xs font-mono overflow-auto overflow-x-auto max-h-32">
                  {JSON.stringify(preferences, null, 2)}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

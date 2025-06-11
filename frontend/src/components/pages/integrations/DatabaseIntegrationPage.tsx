import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Database, ArrowLeft, Plus, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const DatabaseIntegrationPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => navigate('/integrations')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Database className="h-8 w-8 text-blue-600" />
            Database Integration
          </h1>
          <p className="text-muted-foreground">
            Manage database connections and data sources
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Connection
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Database Connections</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-muted-foreground">
            <Database className="h-12 w-12 mx-auto mb-4" />
            <p>No database connections configured</p>
            <Button className="mt-4">
              <Plus className="h-4 w-4 mr-2" />
              Add First Connection
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

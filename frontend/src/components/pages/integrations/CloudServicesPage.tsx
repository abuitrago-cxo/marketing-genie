import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Cloud, ArrowLeft, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const CloudServicesPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => navigate('/integrations')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Cloud className="h-8 w-8 text-purple-600" />
            Cloud Services
          </h1>
          <p className="text-muted-foreground">
            Connect to AWS, Azure, GCP, and other cloud providers
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Provider
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Cloud Providers</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-muted-foreground">
            <Cloud className="h-12 w-12 mx-auto mb-4" />
            <p>No cloud providers configured</p>
            <Button className="mt-4">
              <Plus className="h-4 w-4 mr-2" />
              Connect Provider
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

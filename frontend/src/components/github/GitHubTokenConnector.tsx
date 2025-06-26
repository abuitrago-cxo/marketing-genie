import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { API_ENDPOINTS } from '@/config/api';

export const GitHubTokenConnector: React.FC = () => {
  const [token, setToken] = useState('');
  const [status, setStatus] = useState<'connected' | 'disconnected' | 'error' | 'checking'>('checking');
  const [message, setMessage] = useState('');
  const [saving, setSaving] = useState(false);

  const checkStatus = async () => {
    setStatus('checking');
    try {
      const res = await fetch(API_ENDPOINTS.GITHUB.CONNECTION_STATUS);
      const data = await res.json();
      if (data.status === 'connected') {
        setStatus('connected');
        setMessage('GitHub account connected');
      } else {
        setStatus('disconnected');
        setMessage(data.message || 'Not connected');
      }
    } catch (err) {
      setStatus('error');
      setMessage('Error checking connection');
    }
  };

  useEffect(() => {
    checkStatus();
  }, []);

  const saveToken = async () => {
    if (!token) return;
    setSaving(true);
    try {
      const res = await fetch(API_ENDPOINTS.GITHUB.TOKEN, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });
      const data = await res.json();
      if (res.ok) {
        setToken('');
        await checkStatus();
      } else {
        setStatus('error');
        setMessage(data.detail || 'Failed to save token');
      }
    } catch (e) {
      setStatus('error');
      setMessage('Network error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card className="w-full max-w-xl mx-auto mt-8">
      <CardHeader>
        <CardTitle>Connect GitHub (Personal Access Token)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {status === 'connected' ? (
            <p className="text-green-600 text-sm">{message}</p>
          ) : (
            <>
              <Input
                placeholder="ghp_xxx..."
                value={token}
                onChange={(e) => setToken(e.target.value)}
                disabled={saving}
              />
              <Button onClick={saveToken} disabled={saving || !token}>
                {saving ? 'Saving…' : 'Save Token'}
              </Button>
              {message && <p className="text-sm text-red-500">{message}</p>}
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

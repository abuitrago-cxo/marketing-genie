import React, { useEffect, useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Loader2 } from 'lucide-react';

interface AgentTaskResultsModalProps {
  taskId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

interface TaskStatusResponse {
  success: boolean;
  status: 'pending' | 'completed' | string;
  result: any;
  message?: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1/enhanced';

export const AgentTaskResultsModal: React.FC<AgentTaskResultsModalProps> = ({ taskId, isOpen, onClose }) => {
  const [status, setStatus] = useState<'pending' | 'completed' | 'error' | null>(null);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!taskId || !isOpen) return;

    let interval: NodeJS.Timeout;

    const fetchStatus = async () => {
      try {
        const res = await fetch(`${API_BASE}/agents/tasks/${taskId}`);
        const data: TaskStatusResponse = await res.json();
        if (!data.success) {
          throw new Error(data.message || 'Unknown error');
        }
        setStatus(data.status as any);
        if (data.status === 'completed') {
          setResult(data.result);
          clearInterval(interval);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to get task status');
        setStatus('error');
        clearInterval(interval);
      }
    };

    // first fetch immediately then start interval
    fetchStatus();
    interval = setInterval(fetchStatus, 2000);

    return () => clearInterval(interval);
  }, [taskId, isOpen]);

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Code Engineer Task</DialogTitle>
        </DialogHeader>
        {status === 'pending' && (
          <div className="flex items-center space-x-2 py-4">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Processing...</span>
          </div>
        )}
        {status === 'completed' && (
          <div className="py-4 whitespace-pre-wrap text-sm">
            {typeof result === 'object' ? JSON.stringify(result, null, 2) : String(result)}
          </div>
        )}
        {status === 'error' && (
          <div className="py-4 text-red-600 text-sm">{error}</div>
        )}
      </DialogContent>
    </Dialog>
  );
};

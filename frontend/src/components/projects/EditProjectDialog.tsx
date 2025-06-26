import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
  DialogClose,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Project, UpdateProjectData } from '@/hooks/useProjects';

interface EditProjectDialogProps {
  project: Project | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (id: number, data: UpdateProjectData) => Promise<void>;
}

export const EditProjectDialog: React.FC<EditProjectDialogProps> = ({
  project,
  open,
  onOpenChange,
  onSave,
}) => {
  const [form, setForm] = useState<UpdateProjectData>({});

  useEffect(() => {
    if (project) {
      setForm({
        name: project.name,
        description: project.description,
        github_repo_url: project.github_repo_url,
        status: project.status,
        priority: project.priority,
        team: project.team,
      });
    }
  }, [project]);

  if (!project) return null;

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    await onSave(project.id, form);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Project</DialogTitle>
          <DialogDescription>
            Update the project details and click save when you're done.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <Input
            name="name"
            value={form.name || ''}
            onChange={handleChange}
            placeholder="Project Name"
          />
          <Textarea
            name="description"
            value={form.description || ''}
            onChange={handleChange}
            placeholder="Description"
          />
          <Input
            name="github_repo_url"
            value={form.github_repo_url || ''}
            onChange={handleChange}
            placeholder="GitHub Repository URL"
          />
          <Input
            name="status"
            value={form.status || ''}
            onChange={handleChange}
            placeholder="Status (e.g., active)"
          />
          <Input
            name="priority"
            value={form.priority || ''}
            onChange={handleChange}
            placeholder="Priority (e.g., medium)"
          />
          <Input
            name="team"
            value={form.team || ''}
            onChange={handleChange}
            placeholder="Team (comma separated)"
          />
        </div>

        <DialogFooter className="pt-2">
          <DialogClose asChild>
            <Button variant="secondary">Cancel</Button>
          </DialogClose>
          <Button onClick={handleSave}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// frontend/src/components/ConfigModal.tsx
import React from 'react';
import { useConfig, LLMConfig } from '../contexts/ConfigContext';
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ReloadIcon } from "@radix-ui/react-icons";


interface ConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ConfigModal({ isOpen, onClose }: ConfigModalProps) {
  const { llmConfig, updateConfig, resetToDefaults, isLoading } = useConfig();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    updateConfig({ [name]: type === 'password' ? value : value.trim() });
  };

  const handleSelectChange = (value: string) => {
    updateConfig({ llmProvider: value as LLMConfig["llmProvider"] });
  };

  const handleReset = async () => {
    if (window.confirm("Are you sure you want to reset all settings to their default values? This will fetch the latest defaults from the backend.")) {
      await resetToDefaults();
    }
  };

  if (isLoading || !llmConfig.isLoaded) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Configuration</DialogTitle>
          </DialogHeader>
          <div className="p-4 text-center">
            <ReloadIcon className="mr-2 h-4 w-4 animate-spin inline-block" />
            Loading configuration...
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[525px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>LLM Configuration</DialogTitle>
          <DialogDescription>
            Manage settings for Language Model providers. Changes are saved automatically.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="llmProvider" className="text-right">
              LLM Provider
            </Label>
            <Select
              name="llmProvider"
              value={llmConfig.llmProvider}
              onValueChange={handleSelectChange}
            >
              <SelectTrigger className="col-span-3">
                <SelectValue placeholder="Select a provider" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="gemini">Gemini</SelectItem>
                <SelectItem value="ollama">Ollama</SelectItem>
                <SelectItem value="lmstudio">LM Studio</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {llmConfig.llmProvider === 'gemini' && (
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="geminiApiKey" className="text-right">
                Gemini API Key
              </Label>
              <Input
                id="geminiApiKey"
                name="geminiApiKey"
                type="password"
                value={llmConfig.geminiApiKey}
                onChange={handleInputChange}
                className="col-span-3"
                placeholder="Enter your Gemini API Key"
              />
            </div>
          )}

          {llmConfig.llmProvider === 'ollama' && (
            <>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="ollamaBaseUrl" className="text-right">
                  Ollama URL
                </Label>
                <Input
                  id="ollamaBaseUrl"
                  name="ollamaBaseUrl"
                  value={llmConfig.ollamaBaseUrl}
                  onChange={handleInputChange}
                  className="col-span-3"
                  placeholder="e.g., http://localhost:11434"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="ollamaModelName" className="text-right">
                  Ollama Model
                </Label>
                <Input
                  id="ollamaModelName"
                  name="ollamaModelName"
                  value={llmConfig.ollamaModelName}
                  onChange={handleInputChange}
                  className="col-span-3"
                  placeholder="e.g., llama2"
                />
              </div>
            </>
          )}

          {llmConfig.llmProvider === 'lmstudio' && (
            <>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="lmstudioBaseUrl" className="text-right">
                  LM Studio URL
                </Label>
                <Input
                  id="lmstudioBaseUrl"
                  name="lmstudioBaseUrl"
                  value={llmConfig.lmstudioBaseUrl}
                  onChange={handleInputChange}
                  className="col-span-3"
                  placeholder="e.g., http://localhost:1234/v1"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="lmstudioModelName" className="text-right">
                  LM Studio Model
                </Label>
                <Input
                  id="lmstudioModelName"
                  name="lmstudioModelName"
                  value={llmConfig.lmstudioModelName}
                  onChange={handleInputChange}
                  className="col-span-3"
                  placeholder="e.g., Publisher/Model"
                />
              </div>
            </>
          )}
        </div>
        <DialogFooter className="sm:justify-between">
            <Button type="button" variant="outline" onClick={handleReset}>
                Reset to Defaults
            </Button>
          <DialogClose asChild>
            <Button type="button">Close</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

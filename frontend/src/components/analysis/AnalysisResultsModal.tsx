/**
 * Modal component for displaying analysis results
 * Shows both codebase and documentation analysis results
 */

import React from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  TrendingUp, 
  FileText, 
  Code, 
  Shield, 
  Zap,
  Star,
  Clock
} from 'lucide-react';
import { CodebaseAnalysisResponse, DocumentationAnalysisResponse } from '@/hooks/useProjects';

interface AnalysisResultsModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectName: string;
  codebaseResults?: CodebaseAnalysisResponse;
  documentationResults?: DocumentationAnalysisResponse;
}

const getScoreColor = (score: number) => {
  if (score >= 8) return 'text-green-600';
  if (score >= 6) return 'text-yellow-600';
  return 'text-red-600';
};

const getScoreIcon = (score: number) => {
  if (score >= 8) return <CheckCircle className="h-4 w-4 text-green-600" />;
  if (score >= 6) return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
  return <XCircle className="h-4 w-4 text-red-600" />;
};

export const AnalysisResultsModal: React.FC<AnalysisResultsModalProps> = ({
  isOpen,
  onClose,
  projectName,
  codebaseResults,
  documentationResults
}) => {
  const hasCodebaseResults = codebaseResults?.results;
  const hasDocumentationResults = documentationResults?.results;

  if (!hasCodebaseResults && !hasDocumentationResults) {
    return null;
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Analysis Results - {projectName}
          </DialogTitle>
          <DialogDescription>
            Comprehensive analysis results for your project
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue={hasCodebaseResults ? "codebase" : "documentation"} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            {hasCodebaseResults && (
              <TabsTrigger value="codebase" className="flex items-center gap-2">
                <Code className="h-4 w-4" />
                Codebase Analysis
              </TabsTrigger>
            )}
            {hasDocumentationResults && (
              <TabsTrigger value="documentation" className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Documentation Analysis
              </TabsTrigger>
            )}
          </TabsList>

          {hasCodebaseResults && (
            <TabsContent value="codebase" className="space-y-4">
              <ScrollArea className="h-[500px] pr-4">
                <CodebaseAnalysisResults results={codebaseResults.results!} />
              </ScrollArea>
            </TabsContent>
          )}

          {hasDocumentationResults && (
            <TabsContent value="documentation" className="space-y-4">
              <ScrollArea className="h-[500px] pr-4">
                <DocumentationAnalysisResults results={documentationResults.results!} />
              </ScrollArea>
            </TabsContent>
          )}
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

const CodebaseAnalysisResults: React.FC<{ results: NonNullable<CodebaseAnalysisResponse['results']> }> = ({ results }) => {
  // Explicitly type the findings for each category based on CodebaseAnalysisResponse
  type ArchitectureFindings = NonNullable<NonNullable<CodebaseAnalysisResponse['results']>['findings']['architecture']>;
  type SecurityFindings = NonNullable<NonNullable<CodebaseAnalysisResponse['results']>['findings']['security']>;
  type PerformanceFindings = NonNullable<NonNullable<CodebaseAnalysisResponse['results']>['findings']['performance']>;
  type QualityFindings = NonNullable<NonNullable<CodebaseAnalysisResponse['results']>['findings']['quality']>;
  return (
    <div className="space-y-6">
      {/* Overall Score */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Overall Score</span>
            <div className="flex items-center gap-2">
              {getScoreIcon(results.overall_score)}
              <span className={`text-2xl font-bold ${getScoreColor(results.overall_score)}`}>
                {results.overall_score}/10
              </span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Progress value={results.overall_score * 10} className="w-full" />
          <div className="mt-2 flex justify-between text-sm text-muted-foreground">
            <span>Technology Stack: {results.detected_tech_stack.join(', ')}</span>
            <span>Completed: {new Date(results.completion_time).toLocaleDateString()}</span>
          </div>
        </CardContent>
      </Card>

      {/* Category Scores */}
      <div className="grid grid-cols-2 gap-4">
        {Object.entries(results.findings).map(([category, categorySpecificFindings]) => {
                    const findings = categorySpecificFindings as any; // General access for score, then specific below
          return (
          <Card key={category}>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  {category === 'architecture' && <Code className="h-4 w-4" />}
                  {category === 'security' && <Shield className="h-4 w-4" />}
                  {category === 'performance' && <Zap className="h-4 w-4" />}
                  {category === 'quality' && <Star className="h-4 w-4" />}
                  <span className="capitalize">{category}</span>
                </div>
                <div className="flex items-center gap-1">
                  {getScoreIcon(findings.score)}
                  <span className={`font-bold ${getScoreColor(findings.score)}`}>
                    {findings.score.toFixed(1)}
                  </span>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <Progress value={findings.score * 10} className="mb-3" />
              
              {/* Category-specific content */}
              {category === 'architecture' && (findings as ArchitectureFindings).patterns_found && (
                <div className="mb-2">
                  <p className="text-xs font-medium text-muted-foreground mb-1">Patterns Found:</p>
                  <div className="flex flex-wrap gap-1">
                    {(findings as ArchitectureFindings).patterns_found.map((pattern, idx) => (
                      <Badge key={idx} variant="secondary" className="text-xs">{pattern}</Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {category === 'security' && (findings as SecurityFindings).vulnerabilities && (
                <div className="mb-2">
                  <p className="text-xs font-medium text-muted-foreground mb-1">Vulnerabilities:</p>
                  <ul className="text-xs space-y-1">
                    {(findings as SecurityFindings).vulnerabilities.slice(0, 2).map((vuln, idx) => (
                      <li key={idx} className="text-red-600">• {vuln}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {category === 'performance' && (findings as PerformanceFindings).bottlenecks && (
                <div className="mb-2">
                  <p className="text-xs font-medium text-muted-foreground mb-1">Bottlenecks:</p>
                  <ul className="text-xs space-y-1">
                    {(findings as PerformanceFindings).bottlenecks.slice(0, 2).map((bottleneck, idx) => (
                      <li key={idx} className="text-orange-600">• {bottleneck}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {category === 'quality' && (findings as QualityFindings).metrics && (
                <div className="mb-2">
                  <p className="text-xs font-medium text-muted-foreground mb-1">Metrics:</p>
                  <div className="text-xs">
                    {Object.entries((findings as QualityFindings).metrics).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="capitalize">{key.replace('_', ' ')}:</span>
                        <span>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {findings.recommendations && findings.recommendations.length > 0 && (
                // @ts-ignore TODO: Fix this type, recommendations exist on all findings types

                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">Top Recommendation:</p>
                  <p className="text-xs text-blue-600">{findings.recommendations[0]}</p>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      )}
      </div>
    </div>
  );
};

const DocumentationAnalysisResults: React.FC<{ results: NonNullable<DocumentationAnalysisResponse['results']> }> = ({ results }) => {
  return (
    <div className="space-y-6">
      {/* Overall Score */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Documentation Score</span>
            <div className="flex items-center gap-2">
              {getScoreIcon(results.overall_score)}
              <span className={`text-2xl font-bold ${getScoreColor(results.overall_score)}`}>
                {results.overall_score}/10
              </span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Progress value={results.overall_score * 10} className="w-full" />
          <div className="mt-2 flex justify-between text-sm text-muted-foreground">
            <span>Coverage: {results.analysis_summary.completeness_percentage.toFixed(1)}%</span>
            <span>Documents: {results.analysis_summary.total_documents_found}</span>
          </div>
        </CardContent>
      </Card>

      {/* Summary Metrics */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Structure</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {getScoreIcon(results.analysis_summary.structure_score)}
              <span className={`text-lg font-bold ${getScoreColor(results.analysis_summary.structure_score)}`}>
                {results.analysis_summary.structure_score.toFixed(1)}
              </span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Quality</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {getScoreIcon(results.analysis_summary.quality_score)}
              <span className={`text-lg font-bold ${getScoreColor(results.analysis_summary.quality_score)}`}>
                {results.analysis_summary.quality_score.toFixed(1)}
              </span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Completeness</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-blue-600">
                {results.analysis_summary.completeness_percentage.toFixed(0)}%
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      {results.recommendations && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Priority Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results.recommendations.priority_actions.slice(0, 3).map((action, idx) => (
                <div key={idx} className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                  <Clock className="h-4 w-4 mt-0.5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">{action.action}</p>
                    <div className="flex gap-2 mt-1">
                      <Badge variant={action.priority === 'high' ? 'destructive' : 'secondary'} className="text-xs">
                        {action.priority}
                      </Badge>
                      <Badge variant="outline" className="text-xs">{action.effort}</Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

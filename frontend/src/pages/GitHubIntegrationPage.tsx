import React from 'react';
import { GitHubTokenConnector } from '@/components/github/GitHubTokenConnector';
import { GitHubRepositories } from '@/components/github/GitHubRepositories';

const GitHubIntegrationPage: React.FC = () => {
  return (
    <div className="p-4 md:p-8 space-y-8">
      <GitHubTokenConnector />
      <GitHubRepositories />
    </div>
  );
};

export default GitHubIntegrationPage;

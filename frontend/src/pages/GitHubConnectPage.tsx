import React from 'react';
import { GitHubTokenConnector } from '@/components/github/GitHubTokenConnector';

const GitHubConnectPage: React.FC = () => {
  return (
    <div className="p-4 md:p-8">
      <GitHubTokenConnector />
    </div>
  );
};

export default GitHubConnectPage;

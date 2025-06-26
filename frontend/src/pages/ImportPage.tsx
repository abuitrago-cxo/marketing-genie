import React from 'react';
import { PublicRepoImporter } from '@/components/github/PublicRepoImporter';

const ImportPage: React.FC = () => {
  return (
    <div className="p-4 md:p-8">
      <PublicRepoImporter />
    </div>
  );
};

export default ImportPage;

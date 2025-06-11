import React from "react";
import { BrowserRouter as Router } from "react-router-dom";
import { EnhancedLayout } from "@/components/enhanced/EnhancedLayout";
import { SpecializedAgentToggle } from "@/components/specialized/SpecializedAgentToggle";

// Auth disabled: removed Auth0Provider and UserProfile

function AppContent() {
  const [useSpecializedAgents, setUseSpecializedAgents] = React.useState(false);

  return (
    <EnhancedLayout
      headerActions={
        <div className="flex items-center space-x-4">
          <SpecializedAgentToggle
            enabled={useSpecializedAgents}
            onToggle={setUseSpecializedAgents}
            className="w-80"
          />
        </div>
      }
    />
  );
};

export default function App() {
  return <AppContent />;
}

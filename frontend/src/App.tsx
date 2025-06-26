import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { EnhancedLayout } from "@/components/enhanced/EnhancedLayout";
import { SpecializedAgentToggle } from "@/components/specialized/SpecializedAgentToggle";


import LoginPage from "@/pages/LoginPage";
import TestAuth from "@/pages/TestAuth";
import GitHubConnectPage from "@/pages/GitHubConnectPage";
import GitHubIntegrationPage from "@/pages/GitHubIntegrationPage";
import UserProfile from "@/components/auth/UserProfile";

function AppContent() {
  const [useSpecializedAgents, setUseSpecializedAgents] = React.useState(false);
  const location = useLocation();

  return (
    <EnhancedLayout
      headerActions={
        <div className="flex items-center space-x-4">
          <SpecializedAgentToggle
            enabled={useSpecializedAgents}
            onToggle={setUseSpecializedAgents}
            className="w-80"
          />
          {/* <UserProfile /> */}
        </div>
      }
    />
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/test-auth" element={<TestAuth />} />
      <Route path="/github-connect" element={<GitHubConnectPage />} />
      <Route path="/integrations/github" element={<GitHubIntegrationPage />} />
      <Route
        path="/*"
        element={
          // <ProtectedRoute>
            <AppContent />
          // </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
      <Router basename="/app">
        <AppRoutes />
      </Router>
  );
}

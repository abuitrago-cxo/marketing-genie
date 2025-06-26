import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import useAuth from '@/hooks/useAuth';

const TestAuth: React.FC = () => {
  const { currentUser, loginWithGoogle, loginWithGithub, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center mb-6">Authentication Test</h1>
        
        {currentUser ? (
          <div className="space-y-4">
            <div className="space-y-2">
              <h2 className="text-lg font-semibold">User Information</h2>
              <div className="bg-gray-50 p-4 rounded">
                <p><span className="font-medium">Name:</span> {currentUser.displayName || 'N/A'}</p>
                <p><span className="font-medium">Email:</span> {currentUser.email || 'N/A'}</p>
                <p><span className="font-medium">UID:</span> {currentUser.uid}</p>
                <p><span className="font-medium">Email Verified:</span> {currentUser.emailVerified ? 'Yes' : 'No'}</p>
              </div>
            </div>
            
            <div className="space-y-2">
              <h2 className="text-lg font-semibold">Actions</h2>
              <div className="space-y-2">
                <Button 
                  onClick={logout} 
                  className="w-full"
                  variant="destructive"
                >
                  Sign Out
                </Button>
                <Button 
                  onClick={() => navigate('/')} 
                  className="w-full"
                  variant="outline"
                >
                  Go to App
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-center">Sign In Methods</h2>
            <div className="space-y-3">
              <Button 
                onClick={loginWithGoogle} 
                className="w-full"
                variant="outline"
              >
                Continue with Google
              </Button>
              <Button 
                onClick={loginWithGithub} 
                className="w-full"
                variant="outline"
              >
                Continue with GitHub
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TestAuth;

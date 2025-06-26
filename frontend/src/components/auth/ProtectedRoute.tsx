import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import useAuth from '../../hooks/useAuth';
import { Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

/**
 * A component that protects routes by checking authentication status
 * @param children - The child components to render if authenticated
 * @param requiredRole - Optional role required to access the route
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRole }) => {
  const { currentUser, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  if (!currentUser) {
    // Redirect to login page if not authenticated
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check for required role if specified
  if (requiredRole) {
    // TODO: Implement role-based access control (RBAC) if needed
    // const userRole = currentUser.role; // You'll need to store roles in your auth system
    // if (userRole !== requiredRole) {
    //   return <Navigate to="/unauthorized" state={{ from: location }} replace />;
    // }
  }

  return <>{children}</>;
};

export default ProtectedRoute;

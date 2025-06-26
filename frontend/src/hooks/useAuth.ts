import { useFirebase } from '../contexts/FirebaseContext';

/**
 * Custom hook to access the auth state and authentication methods
 * @returns Authentication state and methods
 */
const useAuth = () => {
  return useFirebase();
};

export default useAuth;

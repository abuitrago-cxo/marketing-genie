import { initializeApp, getApps, getApp, FirebaseApp } from 'firebase/app';
import { getAuth, Auth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

// Your web app's Firebase configuration
const requiredEnvVars = [
  'VITE_FIREBASE_API_KEY',
  'VITE_FIREBASE_AUTH_DOMAIN',
  'VITE_FIREBASE_PROJECT_ID',
  'VITE_FIREBASE_STORAGE_BUCKET',
  'VITE_FIREBASE_MESSAGING_SENDER_ID',
  'VITE_FIREBASE_APP_ID',
  'VITE_FIREBASE_MEASUREMENT_ID',
];

const missingEnvVars = requiredEnvVars.filter(envVar => !import.meta.env[envVar]);

let firebaseConfig: any = null;

if (missingEnvVars.length > 0) {
  console.error(
    'Firebase initialization failed: Missing environment variables:',
    missingEnvVars.join(', ')
  );
  console.error(
    'Please ensure all VITE_FIREBASE_* environment variables are set in your .env file and accessible during the build process.'
  );
} else {
  firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
    measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID,
  };
}

// Initialize Firebase
let app: FirebaseApp | null = null;
let auth: Auth | null = null;
let db: import('firebase/firestore').Firestore | null = null;

if (firebaseConfig && getApps().length === 0) {
  // Initialize Firebase only if config is valid and no apps are initialized
  try {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    // Initialize Firestore
    db = getFirestore(app);
    console.log('Firebase initialized successfully.');
    // Enable persistence for better offline support (optional)
    // import { getReactNativePersistence, initializeAuth } from 'firebase/auth'; // Example for React Native
    // import { browserLocalPersistence, setPersistence } from 'firebase/auth'; // Example for Web
    // await setPersistence(auth, browserLocalPersistence); // Uncomment and adapt if needed
  } catch (error) {
    console.error('Firebase initialization error:', error);
    // Set to null if initialization fails for other reasons
    app = null;
    auth = null;
    db = null;
  }
} else if (firebaseConfig) {
  // If config is valid but app already initialized (e.g., HMR)
  app = getApp();
  auth = getAuth(app);
  db = getFirestore(app);
} else {
  // If firebaseConfig is null due to missing env vars
  console.warn('Firebase configuration is missing. Firebase services will not be available.');
  app = null; // Explicitly set to null or handle as per app's needs
  auth = null;
  db = null;
}

export { app, auth, db };

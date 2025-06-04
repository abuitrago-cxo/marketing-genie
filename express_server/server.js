const express = require('express');
const morgan = require('morgan');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.PORT || 3000;
const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://127.0.0.1:8000'; // Target for API proxy

// Middleware
app.use(morgan('dev'));
app.use(express.json());

// API Proxy: Forward requests from /api to the Python backend
app.use('/api', createProxyMiddleware({
  target: PYTHON_BACKEND_URL,
  changeOrigin: true, // Recommended for virtual hosted sites
  // Optional: You can add pathRewrite if the backend API paths don't include /api
  // pathRewrite: {
  //   '^/api': '', // Uncomment if Python backend doesn't expect /api prefix
  // },
  onError: (err, req, res) => {
    console.error('Proxy error:', err);
    res.writeHead(500, {
      'Content-Type': 'text/plain',
    });
    res.end('Something went wrong with the API proxy.');
  }
}));

// Define the path to the frontend build directory
const frontendDistPath = path.join(__dirname, '../frontend/dist');

// Serve static files from the '/app' path
app.use('/app', express.static(frontendDistPath));

// SPA Fallback: For any other GET request under /app/*, serve index.html
app.get('/app/*', (req, res) => {
  res.sendFile(path.join(frontendDistPath, 'index.html'), (err) => {
    if (err) {
      // If index.html is not found (e.g., frontend not built), send a specific message
      if (err.code === 'ENOENT') {
        res.status(404).send('Frontend not built. Please run the build process for the frontend application.');
      } else {
        res.status(500).send(err.message);
      }
    }
  });
});

// Simple route for testing the server root
app.get('/', (req, res) => {
  res.send('Node.js Express server is running! Visit /app to see the frontend. API requests to /api are proxied.');
});

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}. Frontend accessible at http://localhost:${PORT}/app. API proxying to ${PYTHON_BACKEND_URL}.`);
});

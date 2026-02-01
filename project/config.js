/**
 * VibeCraft Configuration
 * Environment-based configuration for GitHub Pages + Render deployment
 */

const CONFIG = {
  // API URLs - Environment-based configuration
  // For local development: defaults to localhost
  // For GitHub Pages: requires VITE_API_URL and VITE_SOCKET_URL environment variables
  // Or uses relative paths for same-origin requests
  
  // Get API base from environment or use relative path for same-origin
  API_BASE: (() => {
    const envUrl = import.meta.env?.VITE_API_URL;
    if (envUrl) return envUrl;
    // For local development or when behind same proxy
    return '/api';
  })(),
  
  SOCKET_URL: (() => {
    const envUrl = import.meta.env?.VITE_SOCKET_URL;
    if (envUrl) return envUrl;
    // Default to localhost for local development
    return 'http://localhost:3001';
  })(),
  
  // For backward compatibility
  getAuthBase: function() {
    const envUrl = import.meta.env?.VITE_AUTH_URL;
    if (envUrl) return envUrl;
    // If using relative path for API, return same origin
    if (this.API_BASE === '/api' || this.API_BASE === '/api/') {
      return window.location.origin;
    }
    return this.API_BASE.replace('/api', '');
  }
};

// Export for use in other modules
window.CONFIG = CONFIG;


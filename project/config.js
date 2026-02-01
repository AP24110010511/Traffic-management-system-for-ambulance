/**
 * VibeCraft Configuration
 * Environment-based configuration for Render deployment
 */

const CONFIG = {
  // API URLs - default to localhost for local development
  // These will be overridden by environment variables in production
  API_BASE: import.meta.env?.VITE_API_URL || 'http://localhost:5000/api',
  SOCKET_URL: import.meta.env?.VITE_SOCKET_URL || 'http://localhost:3000',
  
  // For backward compatibility
  getAuthBase: function() {
    return import.meta.env?.VITE_AUTH_URL || this.API_BASE.replace('/api', '');
  }
};

// Export for use in other modules
window.CONFIG = CONFIG;


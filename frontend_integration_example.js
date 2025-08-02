/**
 * Frontend State Integration Example - Universal Knowledge Platform
 * 
 * This example demonstrates how to integrate the frontend state API
 * with a React/Next.js frontend for seamless UI state persistence.
 * 
 * Features:
 * - Automatic state loading on component mount
 * - State saving on user interactions
 * - Session-based state isolation
 * - Error handling and fallbacks
 * - Optimistic updates
 * 
 * Authors: Universal Knowledge Platform Engineering Team
 * Version: 1.0.0 (2024-12-28)
 */

// API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Frontend State Manager Class
 * Handles all interactions with the frontend state API
 */
class FrontendStateManager {
    constructor(sessionId, userId = null) {
        this.sessionId = sessionId;
        this.userId = userId;
        this.baseUrl = `${API_BASE_URL}/api/state`;
        this.cache = new Map();
        this.listeners = new Set();
    }

    /**
     * Generate a session ID if not provided
     */
    static generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Get current UI state for the session
     */
    async getState() {
        try {
            const response = await fetch(`${this.baseUrl}/${this.sessionId}`);
            
            if (response.status === 404) {
                // No state exists yet, return empty state
                return {};
            }
            
            if (!response.ok) {
                throw new Error(`Failed to get state: ${response.status}`);
            }
            
            const data = await response.json();
            return data.data?.current_view_state || {};
            
        } catch (error) {
            console.error('Error getting state:', error);
            return {};
        }
    }

    /**
     * Update UI state for the session
     */
    async updateState(newState) {
        try {
            const response = await fetch(`${this.baseUrl}/${this.sessionId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(newState),
            });
            
            if (!response.ok) {
                throw new Error(`Failed to update state: ${response.status}`);
            }
            
            const data = await response.json();
            const updatedState = data.data?.current_view_state || {};
            
            // Update cache
            this.cache.set(this.sessionId, updatedState);
            
            // Notify listeners
            this.notifyListeners(updatedState);
            
            return updatedState;
            
        } catch (error) {
            console.error('Error updating state:', error);
            throw error;
        }
    }

    /**
     * Merge new state with existing state
     */
    async mergeState(newState) {
        try {
            const response = await fetch(`${this.baseUrl}/${this.sessionId}/merge`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(newState),
            });
            
            if (!response.ok) {
                throw new Error(`Failed to merge state: ${response.status}`);
            }
            
            const data = await response.json();
            const mergedState = data.data?.current_view_state || {};
            
            // Update cache
            this.cache.set(this.sessionId, mergedState);
            
            // Notify listeners
            this.notifyListeners(mergedState);
            
            return mergedState;
            
        } catch (error) {
            console.error('Error merging state:', error);
            throw error;
        }
    }

    /**
     * Set a specific value in the state
     */
    async setStateValue(key, value) {
        try {
            const response = await fetch(`${this.baseUrl}/${this.sessionId}/value/${key}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(value),
            });
            
            if (!response.ok) {
                throw new Error(`Failed to set state value: ${response.status}`);
            }
            
            const data = await response.json();
            const updatedState = data.data?.current_view_state || {};
            
            // Update cache
            this.cache.set(this.sessionId, updatedState);
            
            // Notify listeners
            this.notifyListeners(updatedState);
            
            return updatedState;
            
        } catch (error) {
            console.error('Error setting state value:', error);
            throw error;
        }
    }

    /**
     * Get a specific value from the state
     */
    async getStateValue(key, defaultValue = null) {
        try {
            const response = await fetch(`${this.baseUrl}/${this.sessionId}/value/${key}`);
            
            if (response.status === 404) {
                return defaultValue;
            }
            
            if (!response.ok) {
                throw new Error(`Failed to get state value: ${response.status}`);
            }
            
            const data = await response.json();
            return data.data?.value ?? defaultValue;
            
        } catch (error) {
            console.error('Error getting state value:', error);
            return defaultValue;
        }
    }

    /**
     * Clear the session state
     */
    async clearState() {
        try {
            const response = await fetch(`${this.baseUrl}/${this.sessionId}`, {
                method: 'DELETE',
            });
            
            if (!response.ok) {
                throw new Error(`Failed to clear state: ${response.status}`);
            }
            
            // Clear cache
            this.cache.delete(this.sessionId);
            
            // Notify listeners with empty state
            this.notifyListeners({});
            
            return true;
            
        } catch (error) {
            console.error('Error clearing state:', error);
            throw error;
        }
    }

    /**
     * Get session information
     */
    async getSessionInfo() {
        try {
            const response = await fetch(`${this.baseUrl}/${this.sessionId}/info`);
            
            if (response.status === 404) {
                return null;
            }
            
            if (!response.ok) {
                throw new Error(`Failed to get session info: ${response.status}`);
            }
            
            const data = await response.json();
            return data.data;
            
        } catch (error) {
            console.error('Error getting session info:', error);
            return null;
        }
    }

    /**
     * Add a listener for state changes
     */
    addListener(listener) {
        this.listeners.add(listener);
    }

    /**
     * Remove a listener
     */
    removeListener(listener) {
        this.listeners.delete(listener);
    }

    /**
     * Notify all listeners of state changes
     */
    notifyListeners(state) {
        this.listeners.forEach(listener => {
            try {
                listener(state);
            } catch (error) {
                console.error('Error in state listener:', error);
            }
        });
    }
}

/**
 * React Hook for Frontend State Management
 * Provides a simple interface for React components
 */
export function useFrontendState(sessionId, userId = null) {
    const [state, setState] = React.useState({});
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
    
    const stateManager = React.useMemo(() => {
        return new FrontendStateManager(sessionId, userId);
    }, [sessionId, userId]);

    // Load initial state
    React.useEffect(() => {
        let mounted = true;
        
        const loadState = async () => {
            try {
                setLoading(true);
                setError(null);
                
                const initialState = await stateManager.getState();
                
                if (mounted) {
                    setState(initialState);
                }
            } catch (err) {
                if (mounted) {
                    setError(err.message);
                }
            } finally {
                if (mounted) {
                    setLoading(false);
                }
            }
        };

        loadState();

        // Add listener for state changes
        const handleStateChange = (newState) => {
            if (mounted) {
                setState(newState);
            }
        };

        stateManager.addListener(handleStateChange);

        return () => {
            mounted = false;
            stateManager.removeListener(handleStateChange);
        };
    }, [stateManager]);

    // Update state function
    const updateState = React.useCallback(async (newState) => {
        try {
            setError(null);
            const updatedState = await stateManager.updateState(newState);
            setState(updatedState);
            return updatedState;
        } catch (err) {
            setError(err.message);
            throw err;
        }
    }, [stateManager]);

    // Merge state function
    const mergeState = React.useCallback(async (newState) => {
        try {
            setError(null);
            const mergedState = await stateManager.mergeState(newState);
            setState(mergedState);
            return mergedState;
        } catch (err) {
            setError(err.message);
            throw err;
        }
    }, [stateManager]);

    // Set state value function
    const setStateValue = React.useCallback(async (key, value) => {
        try {
            setError(null);
            const updatedState = await stateManager.setStateValue(key, value);
            setState(updatedState);
            return updatedState;
        } catch (err) {
            setError(err.message);
            throw err;
        }
    }, [stateManager]);

    // Clear state function
    const clearState = React.useCallback(async () => {
        try {
            setError(null);
            await stateManager.clearState();
            setState({});
        } catch (err) {
            setError(err.message);
            throw err;
        }
    }, [stateManager]);

    return {
        state,
        loading,
        error,
        updateState,
        mergeState,
        setStateValue,
        clearState,
    };
}

/**
 * Example React Component using Frontend State
 */
export function DashboardComponent() {
    const sessionId = React.useMemo(() => {
        // Get session ID from localStorage or generate new one
        return localStorage.getItem('sessionId') || FrontendStateManager.generateSessionId();
    }, []);

    const {
        state,
        loading,
        error,
        updateState,
        mergeState,
        setStateValue,
        clearState,
    } = useFrontendState(sessionId);

    // Save session ID to localStorage
    React.useEffect(() => {
        localStorage.setItem('sessionId', sessionId);
    }, [sessionId]);

    // Handle sidebar toggle
    const handleSidebarToggle = async () => {
        const currentCollapsed = state.sidebar?.collapsed || false;
        await setStateValue('sidebar', {
            ...state.sidebar,
            collapsed: !currentCollapsed,
        });
    };

    // Handle tab change
    const handleTabChange = async (tabName) => {
        await setStateValue('sidebar', {
            ...state.sidebar,
            active_tab: tabName,
        });
    };

    // Handle theme change
    const handleThemeChange = async (theme) => {
        await setStateValue('user_preferences', {
            ...state.user_preferences,
            theme: theme,
        });
    };

    // Handle query submission
    const handleQuerySubmit = async (query) => {
        const newQueryHistory = [
            ...(state.query_history || []),
            {
                query,
                timestamp: new Date().toISOString(),
                results_count: 0,
            },
        ];

        await mergeState({
            query_history: newQueryHistory,
            current_view: {
                ...state.current_view,
                page: 'search',
            },
        });
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div className={`dashboard ${state.user_preferences?.theme || 'light'}`}>
            {/* Sidebar */}
            <div className={`sidebar ${state.sidebar?.collapsed ? 'collapsed' : ''}`}>
                <button onClick={handleSidebarToggle}>
                    {state.sidebar?.collapsed ? '☰' : '✕'}
                </button>
                
                {!state.sidebar?.collapsed && (
                    <nav>
                        <button
                            className={state.sidebar?.active_tab === 'dashboard' ? 'active' : ''}
                            onClick={() => handleTabChange('dashboard')}
                        >
                            Dashboard
                        </button>
                        <button
                            className={state.sidebar?.active_tab === 'search' ? 'active' : ''}
                            onClick={() => handleTabChange('search')}
                        >
                            Search
                        </button>
                    </nav>
                )}
            </div>

            {/* Main Content */}
            <div className="main-content">
                <header>
                    <h1>Knowledge Platform</h1>
                    <div className="controls">
                        <select
                            value={state.user_preferences?.theme || 'light'}
                            onChange={(e) => handleThemeChange(e.target.value)}
                        >
                            <option value="light">Light Theme</option>
                            <option value="dark">Dark Theme</option>
                        </select>
                        <button onClick={clearState}>Clear State</button>
                    </div>
                </header>

                {/* Query History */}
                {state.query_history && state.query_history.length > 0 && (
                    <div className="query-history">
                        <h3>Recent Queries</h3>
                        <ul>
                            {state.query_history.map((query, index) => (
                                <li key={index}>
                                    {query.query} - {new Date(query.timestamp).toLocaleString()}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Current View */}
                <div className="current-view">
                    <h2>Current Page: {state.current_view?.page || 'dashboard'}</h2>
                    {state.current_view?.filters && (
                        <div className="filters">
                            <h3>Active Filters:</h3>
                            <pre>{JSON.stringify(state.current_view.filters, null, 2)}</pre>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

/**
 * Example usage in Next.js app
 */
export default function App() {
    return (
        <div className="app">
            <DashboardComponent />
        </div>
    );
}

/**
 * Example CSS for the dashboard
 */
const styles = `
.dashboard {
    display: flex;
    height: 100vh;
}

.dashboard.light {
    background-color: #ffffff;
    color: #333333;
}

.dashboard.dark {
    background-color: #1a1a1a;
    color: #ffffff;
}

.sidebar {
    width: 250px;
    background-color: #f5f5f5;
    border-right: 1px solid #ddd;
    transition: width 0.3s ease;
}

.sidebar.collapsed {
    width: 60px;
}

.sidebar button {
    width: 100%;
    padding: 10px;
    border: none;
    background: none;
    cursor: pointer;
}

.sidebar button:hover {
    background-color: #e0e0e0;
}

.sidebar button.active {
    background-color: #007bff;
    color: white;
}

.main-content {
    flex: 1;
    padding: 20px;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.controls {
    display: flex;
    gap: 10px;
}

.query-history {
    margin-bottom: 20px;
}

.query-history ul {
    list-style: none;
    padding: 0;
}

.query-history li {
    padding: 5px 0;
    border-bottom: 1px solid #eee;
}

.current-view {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 5px;
}

.filters pre {
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 3px;
    overflow-x: auto;
}
`;

// Export the styles for use in your app
export { styles }; 
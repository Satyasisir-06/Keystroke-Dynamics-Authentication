/**
 * KeyAuth — API Client
 * Handles all communication with the FastAPI backend
 */

const API_BASE = '/api';

async function request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    };

    // Add auth token if available
    const token = localStorage.getItem('keyauth_token');
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong');
    }

    return data;
}

export const api = {
    // Registration & Enrollment
    register: (username, name, keystrokes, deviceType = 'web') =>
        request('/register', {
            method: 'POST',
            body: JSON.stringify({ username, name, keystrokes, device_type: deviceType }),
        }),

    enroll: (username, keystrokes, deviceType = 'web') =>
        request('/enroll', {
            method: 'POST',
            body: JSON.stringify({ username, keystrokes, device_type: deviceType }),
        }),

    getEnrollmentStatus: (username) =>
        request(`/enrollment-status/${username}`),

    // Authentication
    authenticate: (username, keystrokes, deviceType = 'web') =>
        request('/authenticate', {
            method: 'POST',
            body: JSON.stringify({ username, keystrokes, device_type: deviceType }),
        }),

    // User (requires JWT)
    getProfile: () => request('/user/profile'),
    getAuthHistory: () => request('/user/auth-history'),
};

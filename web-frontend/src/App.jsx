/**
 * KeyAuth — Main App
 * Root component with routing and auth state management
 */
import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';

export default function App() {
    const [user, setUser] = useState(null);

    useEffect(() => {
        // Check for existing session
        const token = localStorage.getItem('keyauth_token');
        const username = localStorage.getItem('keyauth_username');
        if (token && username) {
            setUser(username);
        }
    }, []);

    const handleLogin = (username) => {
        setUser(username);
    };

    const handleLogout = () => {
        setUser(null);
        localStorage.removeItem('keyauth_token');
        localStorage.removeItem('keyauth_username');
    };

    return (
        <BrowserRouter>
            <Navbar user={user} onLogout={handleLogout} />
            <Routes>
                <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} replace />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
                <Route
                    path="/dashboard"
                    element={user ? <DashboardPage /> : <Navigate to="/login" replace />}
                />
            </Routes>
        </BrowserRouter>
    );
}

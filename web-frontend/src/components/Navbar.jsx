/**
 * KeyAuth — Navbar Component
 */
import { Link, useLocation, useNavigate } from 'react-router-dom';

export default function Navbar({ user, onLogout }) {
    const location = useLocation();
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('keyauth_token');
        if (onLogout) onLogout();
        navigate('/login');
    };

    return (
        <nav className="navbar">
            <Link to="/" className="navbar-logo">
                <img src="/logo.svg" alt="KeyAuth" />
                KeyAuth
            </Link>
            <div className="navbar-links">
                {user ? (
                    <>
                        <Link to="/dashboard" className={location.pathname === '/dashboard' ? 'active' : ''}>
                            Dashboard
                        </Link>
                        <button
                            onClick={handleLogout}
                            className="btn btn-outline"
                            style={{ padding: '8px 20px', fontSize: '0.85rem' }}
                        >
                            Logout
                        </button>
                    </>
                ) : (
                    <>
                        <Link to="/register" className={location.pathname === '/register' ? 'active' : ''}>
                            Register
                        </Link>
                        <Link to="/login" className={location.pathname === '/login' ? 'active' : ''}>
                            <button className="btn btn-primary" style={{ padding: '8px 20px', fontSize: '0.85rem' }}>
                                Login
                            </button>
                        </Link>
                    </>
                )}
            </div>
        </nav>
    );
}

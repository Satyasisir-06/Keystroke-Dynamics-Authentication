/**
 * KeyAuth — Login Page
 * Authenticate by typing the phrase — confidence gauge shows result
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useKeystrokeCapture } from '../hooks/useKeystrokeCapture';
import TypingMetrics from '../components/TypingMetrics';
import ConfidenceGauge from '../components/ConfidenceGauge';
import { api } from '../api/client';

export default function LoginPage({ onLogin }) {
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [result, setResult] = useState(null); // { authenticated, confidence_score, message }

    const {
        keystrokes, typedText, metrics, isComplete,
        handleKeyDown, handleKeyUp, reset, targetPhrase,
    } = useKeystrokeCapture();

    const handleAuthenticate = async () => {
        if (!username.trim()) {
            setError('Please enter your username');
            return;
        }
        if (!isComplete || keystrokes.length < 5) return;

        setLoading(true);
        setError('');
        setResult(null);

        try {
            const res = await api.authenticate(username.trim(), keystrokes);
            setResult(res);

            if (res.authenticated && res.token) {
                localStorage.setItem('keyauth_token', res.token);
                localStorage.setItem('keyauth_username', username.trim());
                if (onLogin) onLogin(username.trim());
                setTimeout(() => navigate('/dashboard'), 2000);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        reset();
        setResult(null);
        setError('');
    };

    return (
        <div className="page-container">
            <div className="auth-card glass-card animate-in">
                {/* Header */}
                <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                    <div style={{
                        width: '64px', height: '64px', margin: '0 auto 16px',
                        borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: 'rgba(0, 212, 255, 0.1)', border: '2px solid rgba(0, 212, 255, 0.2)',
                    }}>
                        <img src="/logo.svg" alt="KeyAuth" style={{ width: '40px', height: '40px' }} />
                    </div>
                    <h1 style={{
                        fontSize: '1.8rem', fontWeight: 800, marginBottom: '8px',
                        background: 'var(--gradient-accent)',
                        WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                    }}>
                        Authenticate with Your Typing
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
                        Type the phrase below. Your typing rhythm is your password.
                    </p>
                </div>

                {/* Username Input */}
                <div style={{ marginBottom: '20px' }}>
                    <label className="input-label">Username</label>
                    <input
                        className="input-field"
                        type="text"
                        placeholder="Enter your username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        autoFocus
                    />
                </div>

                {/* Phrase */}
                <div style={{ marginBottom: '16px' }}>
                    <label className="input-label">Type This Phrase</label>
                    <div className="phrase-card">"{targetPhrase}"</div>
                </div>

                {/* Typing Area */}
                <div style={{ marginBottom: '16px' }}>
                    <textarea
                        className={`typing-area ${result ? (result.authenticated ? 'success' : 'error') : ''}`}
                        placeholder="Start typing to authenticate..."
                        value={typedText}
                        onKeyDown={handleKeyDown}
                        onKeyUp={handleKeyUp}
                        onChange={() => { }}
                    />
                </div>

                {/* Live Metrics */}
                <div style={{ marginBottom: '24px' }}>
                    <TypingMetrics metrics={metrics} />
                </div>

                {/* Confidence Gauge (shown after authentication) */}
                {result && (
                    <div className="animate-in" style={{ marginBottom: '24px' }}>
                        <ConfidenceGauge score={result.confidence_score} />
                        <div style={{ textAlign: 'center', marginTop: '16px' }}>
                            <span className={`status-badge ${result.authenticated ? 'success' : 'error'}`}>
                                {result.authenticated ? '✅ Identity Verified' : '❌ Authentication Failed'}
                            </span>
                            <p style={{
                                color: 'var(--text-secondary)', fontSize: '0.85rem',
                                marginTop: '8px',
                            }}>
                                {result.message}
                            </p>
                        </div>
                    </div>
                )}

                {/* Action Buttons */}
                <div style={{ display: 'flex', gap: '12px' }}>
                    {!result ? (
                        <button
                            className="btn btn-primary btn-full"
                            onClick={handleAuthenticate}
                            disabled={!isComplete || loading || !username.trim()}
                        >
                            {loading ? '⏳ Analyzing...' : isComplete ? '🔓 Verify Identity' : '⌨️ Keep Typing...'}
                        </button>
                    ) : (
                        <>
                            {!result.authenticated && (
                                <button className="btn btn-primary btn-full" onClick={handleReset}>
                                    🔄 Try Again
                                </button>
                            )}
                            {result.authenticated && (
                                <button className="btn btn-primary btn-full" onClick={() => navigate('/dashboard')}>
                                    📊 Go to Dashboard →
                                </button>
                            )}
                        </>
                    )}
                </div>

                {/* Error */}
                {error && (
                    <div className="status-badge error" style={{ width: '100%', marginTop: '16px', justifyContent: 'center' }}>
                        ❌ {error}
                    </div>
                )}

                {/* Footer */}
                <p style={{ textAlign: 'center', marginTop: '24px', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                    Not enrolled yet? <Link to="/register">Register</Link>
                </p>
            </div>
        </div>
    );
}

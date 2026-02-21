/**
 * KeyAuth — Register Page
 * User registration + keystroke enrollment with real-time metrics
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useKeystrokeCapture } from '../hooks/useKeystrokeCapture';
import TypingMetrics from '../components/TypingMetrics';
import { api } from '../api/client';

export default function RegisterPage() {
    const navigate = useNavigate();
    const [step, setStep] = useState(1); // 1 = profile, 2 = enrollment
    const [name, setName] = useState('');
    const [username, setUsername] = useState('');
    const [sampleCount, setSampleCount] = useState(0);
    const [samplesRequired] = useState(5);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [enrolled, setEnrolled] = useState(false);

    const {
        keystrokes, typedText, metrics, isComplete,
        handleKeyDown, handleKeyUp, reset, targetPhrase,
    } = useKeystrokeCapture();

    const handleProfileSubmit = (e) => {
        e.preventDefault();
        if (!name.trim() || !username.trim()) {
            setError('Please fill in both fields');
            return;
        }
        setError('');
        setStep(2);
    };

    const handleSubmitSample = async () => {
        if (!isComplete || keystrokes.length < 5) return;

        setLoading(true);
        setError('');

        try {
            let result;
            if (sampleCount === 0) {
                // First sample → register
                result = await api.register(username.trim(), name.trim(), keystrokes);
            } else {
                // Additional samples → enroll
                result = await api.enroll(username.trim(), keystrokes);
            }

            setSampleCount(result.samples_collected);
            setSuccess(result.message);

            if (result.is_enrolled) {
                setEnrolled(true);
                setTimeout(() => navigate('/login'), 3000);
            } else {
                reset();
                setTimeout(() => setSuccess(''), 3000);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const progress = (sampleCount / samplesRequired) * 100;

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
                        Create Your Identity
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
                        {step === 1 ? 'Set up your profile to get started' : 'Type the phrase to train your pattern'}
                    </p>
                </div>

                {/* Step Indicator */}
                <div style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    gap: '12px', marginBottom: '28px',
                }}>
                    <div style={{
                        width: '36px', height: '36px', borderRadius: '50%',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '0.85rem', fontWeight: 700,
                        background: step >= 1 ? 'var(--gradient-cyan)' : 'rgba(255,255,255,0.06)',
                        color: step >= 1 ? '#0a0e1a' : 'var(--text-muted)',
                    }}>1</div>
                    <div style={{
                        width: '60px', height: '2px',
                        background: step >= 2 ? 'var(--cyan)' : 'rgba(255,255,255,0.08)',
                    }} />
                    <div style={{
                        width: '36px', height: '36px', borderRadius: '50%',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '0.85rem', fontWeight: 700,
                        background: step >= 2 ? 'var(--gradient-cyan)' : 'rgba(255,255,255,0.06)',
                        color: step >= 2 ? '#0a0e1a' : 'var(--text-muted)',
                    }}>2</div>
                </div>

                {/* Step 1: Profile */}
                {step === 1 && (
                    <form onSubmit={handleProfileSubmit} className="animate-in">
                        <div style={{ marginBottom: '20px' }}>
                            <label className="input-label">Full Name</label>
                            <input
                                className="input-field"
                                type="text"
                                placeholder="Enter your full name"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                autoFocus
                            />
                        </div>
                        <div style={{ marginBottom: '24px' }}>
                            <label className="input-label">Username</label>
                            <input
                                className="input-field"
                                type="text"
                                placeholder="Choose a unique username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            />
                        </div>
                        <button type="submit" className="btn btn-primary btn-full">
                            Continue to Enrollment →
                        </button>
                    </form>
                )}

                {/* Step 2: Enrollment */}
                {step === 2 && !enrolled && (
                    <div className="animate-in">
                        {/* Phrase to type */}
                        <div style={{ marginBottom: '16px' }}>
                            <label className="input-label">Type This Phrase</label>
                            <div className="phrase-card">"{targetPhrase}"</div>
                        </div>

                        {/* Typing area */}
                        <div style={{ marginBottom: '16px', position: 'relative' }}>
                            <textarea
                                className={`typing-area ${isComplete ? 'success' : ''}`}
                                placeholder="Start typing the phrase above..."
                                value={typedText}
                                onKeyDown={handleKeyDown}
                                onKeyUp={handleKeyUp}
                                onChange={() => { }} // controlled by hook
                                autoFocus
                            />
                        </div>

                        {/* Live Metrics */}
                        <div style={{ marginBottom: '20px' }}>
                            <TypingMetrics metrics={metrics} />
                        </div>

                        {/* Progress */}
                        <div style={{ marginBottom: '20px' }}>
                            <div style={{
                                display: 'flex', justifyContent: 'space-between',
                                fontSize: '0.85rem', marginBottom: '8px',
                            }}>
                                <span style={{ color: 'var(--text-secondary)' }}>Enrollment Progress</span>
                                <span style={{ color: 'var(--cyan)', fontWeight: 600 }}>
                                    {sampleCount} of {samplesRequired}
                                </span>
                            </div>
                            <div className="progress-bar">
                                <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
                            </div>
                        </div>

                        {/* Submit */}
                        <button
                            className="btn btn-primary btn-full"
                            onClick={handleSubmitSample}
                            disabled={!isComplete || loading}
                        >
                            {loading ? '⏳ Processing...' : isComplete ? '✅ Submit Sample' : '⌨️ Keep Typing...'}
                        </button>
                    </div>
                )}

                {/* Enrolled Success */}
                {enrolled && (
                    <div className="animate-in" style={{ textAlign: 'center', padding: '20px 0' }}>
                        <div style={{ fontSize: '4rem', marginBottom: '16px' }}>🎉</div>
                        <h2 style={{ color: 'var(--green)', marginBottom: '8px' }}>Enrollment Complete!</h2>
                        <p style={{ color: 'var(--text-secondary)' }}>
                            Your typing pattern has been learned. Redirecting to login...
                        </p>
                    </div>
                )}

                {/* Error/Success Messages */}
                {error && (
                    <div className="status-badge error" style={{ width: '100%', marginTop: '16px', justifyContent: 'center' }}>
                        ❌ {error}
                    </div>
                )}
                {success && !enrolled && (
                    <div className="status-badge success" style={{ width: '100%', marginTop: '16px', justifyContent: 'center' }}>
                        ✅ {success}
                    </div>
                )}

                {/* Footer link */}
                <p style={{ textAlign: 'center', marginTop: '24px', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                    Already enrolled? <Link to="/login">Log in</Link>
                </p>
            </div>
        </div>
    );
}

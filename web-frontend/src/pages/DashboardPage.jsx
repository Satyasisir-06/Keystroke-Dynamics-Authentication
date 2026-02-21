/**
 * KeyAuth — Dashboard Page
 * Protected page showing user profile, auth history, and stats
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';

export default function DashboardPage() {
    const navigate = useNavigate();
    const [profile, setProfile] = useState(null);
    const [history, setHistory] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const token = localStorage.getItem('keyauth_token');
        if (!token) {
            navigate('/login');
            return;
        }
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const [profileData, historyData] = await Promise.all([
                api.getProfile(),
                api.getAuthHistory(),
            ]);
            setProfile(profileData);
            setHistory(historyData);
        } catch (err) {
            setError(err.message);
            if (err.message.includes('Invalid') || err.message.includes('expired')) {
                localStorage.removeItem('keyauth_token');
                navigate('/login');
            }
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="page-container" style={{ justifyContent: 'center' }}>
                <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', marginBottom: '12px', animation: 'pulse-glow 2s infinite' }}>⏳</div>
                    <p style={{ color: 'var(--text-secondary)' }}>Loading dashboard...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="page-container" style={{ justifyContent: 'center' }}>
                <div className="auth-card glass-card" style={{ textAlign: 'center' }}>
                    <p style={{ color: 'var(--red)' }}>❌ {error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="page-container" style={{ alignItems: 'stretch' }}>
            <div className="dashboard-grid">
                {/* ── Left Column: Profile ────────────────────────── */}
                <div>
                    <div className="glass-card animate-in" style={{ padding: '28px', textAlign: 'center' }}>
                        {/* Avatar */}
                        <div style={{
                            width: '80px', height: '80px', borderRadius: '50%', margin: '0 auto 16px',
                            background: 'var(--gradient-accent)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: '2rem', fontWeight: 800, color: '#0a0e1a',
                        }}>
                            {profile?.name?.charAt(0)?.toUpperCase() || '?'}
                        </div>
                        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '4px' }}>
                            {profile?.name}
                        </h2>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '20px' }}>
                            @{profile?.username}
                        </p>

                        {/* Info rows */}
                        <div style={{ textAlign: 'left' }}>
                            {[
                                { label: 'Device', value: profile?.device_type || 'web' },
                                { label: 'Enrolled', value: profile?.is_enrolled ? '✅ Yes' : '❌ No' },
                                { label: 'Samples', value: profile?.enrollment_samples },
                                { label: 'Joined', value: new Date(profile?.created_at).toLocaleDateString() },
                            ].map((item, i) => (
                                <div key={i} style={{
                                    display: 'flex', justifyContent: 'space-between', padding: '10px 0',
                                    borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: '0.85rem',
                                }}>
                                    <span style={{ color: 'var(--text-muted)' }}>{item.label}</span>
                                    <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{item.value}</span>
                                </div>
                            ))}
                        </div>

                        {/* Security Score */}
                        {profile?.security_score != null && (
                            <div style={{ marginTop: '24px' }}>
                                <div style={{
                                    width: '100px', height: '100px', borderRadius: '50%',
                                    margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    border: `3px solid ${profile.security_score >= 80 ? 'var(--green)' : profile.security_score >= 50 ? 'var(--yellow)' : 'var(--red)'}`,
                                    boxShadow: `0 0 20px ${profile.security_score >= 80 ? 'var(--green-glow)' : 'var(--red-glow)'}`,
                                }}>
                                    <div style={{ textAlign: 'center' }}>
                                        <div style={{
                                            fontSize: '1.5rem', fontWeight: 800,
                                            color: profile.security_score >= 80 ? 'var(--green)' : profile.security_score >= 50 ? 'var(--yellow)' : 'var(--red)',
                                        }}>
                                            {Math.round(profile.security_score)}%
                                        </div>
                                        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                                            Security
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* ── Middle Column: Auth History ─────────────────── */}
                <div>
                    <div className="glass-card animate-in animate-delay-1" style={{ padding: '28px' }}>
                        <h3 style={{
                            fontSize: '1.1rem', fontWeight: 700, marginBottom: '20px',
                            display: 'flex', alignItems: 'center', gap: '8px',
                        }}>
                            📋 Authentication History
                        </h3>

                        {history?.history?.length > 0 ? (
                            <div>
                                {history.history.map((log, i) => (
                                    <div key={log.id} className="auth-history-item" style={{
                                        animation: `slideIn 0.3s ease ${i * 0.05}s both`,
                                    }}>
                                        <div>
                                            <div className="auth-history-time">
                                                {new Date(log.timestamp).toLocaleString()}
                                            </div>
                                            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                                {log.device_type} {log.ip_address ? `• ${log.ip_address}` : ''}
                                            </div>
                                        </div>
                                        <div className="auth-history-score" style={{
                                            color: log.confidence_score >= 85 ? 'var(--green)' : log.confidence_score >= 60 ? 'var(--yellow)' : 'var(--red)',
                                        }}>
                                            {log.confidence_score}%
                                        </div>
                                        <div className="auth-history-result" style={{
                                            color: log.result === 'accepted' ? 'var(--green)' : 'var(--red)',
                                        }}>
                                            {log.result === 'accepted' ? '✅' : '❌'}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px 0' }}>
                                No authentication attempts yet.
                            </p>
                        )}
                    </div>
                </div>

                {/* ── Right Column: Stats ────────────────────────── */}
                <div>
                    <div className="glass-card animate-in animate-delay-2" style={{ padding: '28px' }}>
                        <h3 style={{
                            fontSize: '1.1rem', fontWeight: 700, marginBottom: '20px',
                            display: 'flex', alignItems: 'center', gap: '8px',
                        }}>
                            📊 Quick Stats
                        </h3>

                        <div style={{ display: 'grid', gap: '12px' }}>
                            {[
                                { label: 'Total Logins', value: history?.total_attempts || 0, icon: '🔑' },
                                { label: 'Success Rate', value: `${history?.success_rate || 0}%`, icon: '✅' },
                                { label: 'Avg Confidence', value: `${history?.avg_confidence || 0}%`, icon: '🎯' },
                                { label: 'Enrolled Samples', value: profile?.enrollment_samples || 0, icon: '📝' },
                            ].map((stat, i) => (
                                <div key={i} style={{
                                    padding: '16px', borderRadius: 'var(--radius-sm)',
                                    background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)',
                                    display: 'flex', alignItems: 'center', gap: '12px',
                                }}>
                                    <span style={{ fontSize: '1.5rem' }}>{stat.icon}</span>
                                    <div>
                                        <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--cyan)' }}>{stat.value}</div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>{stat.label}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

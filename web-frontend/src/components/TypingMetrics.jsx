/**
 * KeyAuth — TypingMetrics Component
 * Real-time stat pills for dwell time, flight time, and speed
 */
export default function TypingMetrics({ metrics }) {
    return (
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'center' }}>
            <div className="stat-pill">
                ⏱️ Dwell: <span className="value">{metrics.dwellTime}ms</span>
            </div>
            <div className="stat-pill">
                ✈️ Flight: <span className="value">{metrics.flightTime}ms</span>
            </div>
            <div className="stat-pill">
                ⚡ Speed: <span className="value">{metrics.speed} chars/s</span>
            </div>
        </div>
    );
}

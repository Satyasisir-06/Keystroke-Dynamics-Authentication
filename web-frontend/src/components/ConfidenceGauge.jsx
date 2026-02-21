/**
 * KeyAuth — Confidence Gauge Component
 * SVG circular gauge showing authentication confidence score
 */
export default function ConfidenceGauge({ score, size = 180 }) {
    const percentage = Math.round(score * 100);
    const radius = (size - 20) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score * circumference);

    // Color based on score
    let color, label;
    if (percentage >= 85) {
        color = '#22c55e';
        label = 'Verified';
    } else if (percentage >= 60) {
        color = '#eab308';
        label = 'Uncertain';
    } else {
        color = '#ef4444';
        label = 'Rejected';
    }

    return (
        <div className="gauge-container">
            <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
                {/* Background ring */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke="rgba(255,255,255,0.06)"
                    strokeWidth="8"
                />
                {/* Score ring */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={color}
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    style={{
                        transition: 'stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.3s ease',
                        filter: `drop-shadow(0 0 8px ${color}40)`,
                    }}
                />
                {/* Center text */}
                <text
                    x={size / 2}
                    y={size / 2}
                    textAnchor="middle"
                    dominantBaseline="central"
                    style={{
                        transform: 'rotate(90deg)',
                        transformOrigin: `${size / 2}px ${size / 2}px`,
                        fill: color,
                        fontSize: `${size * 0.22}px`,
                        fontWeight: 800,
                        fontFamily: 'Inter, sans-serif',
                    }}
                >
                    {percentage}%
                </text>
            </svg>
            <div className="gauge-label" style={{ color }}>{label}</div>
        </div>
    );
}

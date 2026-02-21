/**
 * KeyAuth — useKeystrokeCapture Hook
 * Captures keydown/keyup events with high-resolution timestamps
 * and builds an array of KeystrokeEvent objects for the backend.
 */
import { useState, useCallback, useRef } from 'react';

const TARGET_PHRASE = 'the quick brown fox jumps over the lazy dog';

export function useKeystrokeCapture() {
    const [keystrokes, setKeystrokes] = useState([]);
    const [typedText, setTypedText] = useState('');
    const [isCapturing, setIsCapturing] = useState(false);
    const [metrics, setMetrics] = useState({ dwellTime: 0, flightTime: 0, speed: 0 });
    const pendingKeys = useRef({});
    const lastReleaseTime = useRef(null);

    const reset = useCallback(() => {
        setKeystrokes([]);
        setTypedText('');
        setIsCapturing(false);
        setMetrics({ dwellTime: 0, flightTime: 0, speed: 0 });
        pendingKeys.current = {};
        lastReleaseTime.current = null;
    }, []);

    const handleKeyDown = useCallback((e) => {
        // Ignore modifier keys and special keys
        if (e.key.length > 1 && e.key !== 'Backspace' && e.key !== ' ') return;
        if (e.ctrlKey || e.metaKey || e.altKey) return;
        if (e.repeat) return; // Ignore key repeat

        const now = performance.now();
        const key = e.key === ' ' ? 'Space' : e.key;

        if (!isCapturing) setIsCapturing(true);

        // Store press time for this key
        pendingKeys.current[key] = now;
    }, [isCapturing]);

    const handleKeyUp = useCallback((e) => {
        if (e.key.length > 1 && e.key !== 'Backspace' && e.key !== ' ') return;
        if (e.ctrlKey || e.metaKey || e.altKey) return;

        const now = performance.now();
        const key = e.key === ' ' ? 'Space' : e.key;

        const pressTime = pendingKeys.current[key];
        if (pressTime === undefined) return;
        delete pendingKeys.current[key];

        // Handle backspace
        if (e.key === 'Backspace') {
            setTypedText(prev => prev.slice(0, -1));
            return;
        }

        // Build keystroke event
        const event = {
            key: e.key,
            press_time: pressTime,
            release_time: now,
        };

        setKeystrokes(prev => {
            const updated = [...prev, event];

            // Calculate live metrics
            if (updated.length >= 2) {
                const dwellTimes = updated.map(k => k.release_time - k.press_time);
                const avgDwell = dwellTimes.reduce((a, b) => a + b, 0) / dwellTimes.length;

                const flightTimes = [];
                for (let i = 1; i < updated.length; i++) {
                    flightTimes.push(updated[i].press_time - updated[i - 1].release_time);
                }
                const avgFlight = flightTimes.length > 0
                    ? flightTimes.reduce((a, b) => a + b, 0) / flightTimes.length
                    : 0;

                const totalTime = (updated[updated.length - 1].release_time - updated[0].press_time) / 1000;
                const speed = totalTime > 0 ? (updated.length / totalTime).toFixed(1) : 0;

                setMetrics({
                    dwellTime: Math.round(avgDwell),
                    flightTime: Math.round(avgFlight),
                    speed: parseFloat(speed),
                });
            }

            return updated;
        });

        setTypedText(prev => prev + e.key);
        lastReleaseTime.current = now;
    }, []);

    const isComplete = typedText.toLowerCase() === TARGET_PHRASE;

    return {
        keystrokes,
        typedText,
        isCapturing,
        metrics,
        isComplete,
        handleKeyDown,
        handleKeyUp,
        reset,
        targetPhrase: TARGET_PHRASE,
    };
}

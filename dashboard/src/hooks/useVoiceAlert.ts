import { useEffect, useRef, useState } from 'react';

export function useVoiceAlert(isEnabled: boolean = true) {
    const [supported, setSupported] = useState(false);
    const lastSpokenRef = useRef<Record<string, number>>({});

    useEffect(() => {
        if ('speechSynthesis' in window) {
            setSupported(true);
        }
    }, []);

    const speak = (workerName: string, riskType: 'Fatigue' | 'Ergonomic') => {
        if (!supported || !isEnabled) return;

        // Debounce logic: Only speak maximum once every 2 minutes per worker per risk
        const key = `${workerName}-${riskType}`;
        const now = Date.now();
        const lastSpoken = lastSpokenRef.current[key] || 0;

        if (now - lastSpoken < 120000) {
            return;
        }

        lastSpokenRef.current[key] = now;

        const utterance = new SpeechSynthesisUtterance(
            `Attention Supervisor: ${workerName} is exhibiting high ${riskType} risk.`
        );

        // Optional: Pick a professional-sounding voice if available
        const voices = window.speechSynthesis.getVoices();
        const preferredVoice = voices.find(v => v.lang === 'en-US' && v.name.includes('Google'));
        if (preferredVoice) utterance.voice = preferredVoice;

        utterance.rate = 1.0;
        utterance.pitch = 1.1; // Slightly urgent pitch

        window.speechSynthesis.speak(utterance);
    };

    return { speak, supported };
}

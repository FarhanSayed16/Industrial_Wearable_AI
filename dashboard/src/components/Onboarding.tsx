import { useState, useEffect } from 'react';
import { X, ChevronRight, Check } from 'lucide-react';

export function Onboarding() {
    const [isVisible, setIsVisible] = useState(false);
    const [step, setStep] = useState(0);

    const steps = [
        { title: "Welcome to Industrial Wearable AI", content: "This dashboard lets you monitor factory worker ergonomics and productivity in real-time." },
        { title: "Live View", content: "The Live View updates instantly from Edge Gateways, showing worker posture and fatigue risks as they happen." },
        { title: "Keyboard Shortcuts", content: "Pro tip: Use Ctrl+1 for Live View, Ctrl+2 for Sessions, and Ctrl+3 for Analytics to navigate quickly." }
    ];

    useEffect(() => {
        const hasSeen = localStorage.getItem('hasSeenOnboarding');
        if (!hasSeen) {
            // Slight delay so it doesn't pop up immediately on first paint
            const t = setTimeout(() => setIsVisible(true), 1000);
            return () => clearTimeout(t);
        }
    }, []);

    const handleClose = () => {
        setIsVisible(false);
        localStorage.setItem('hasSeenOnboarding', 'true');
    };

    const nextStep = () => {
        if (step < steps.length - 1) {
            setStep(s => s + 1);
        } else {
            handleClose();
        }
    };

    if (!isVisible) return null;

    return (
        <div style={{ position: 'fixed', bottom: '2rem', right: '2rem', width: '300px', backgroundColor: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-lg)', border: '1px solid var(--color-border)', zIndex: 9999, overflow: 'hidden' }}>
            <div style={{ padding: '1rem', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-primary)' }}>{steps[step].title}</h3>
                <button onClick={handleClose} style={{ background: 'none', border: 'none', padding: '0.25rem', minWidth: 'auto', color: 'var(--color-text-muted)' }}>
                    <X size={16} />
                </button>
            </div>
            <div style={{ padding: '1rem', fontSize: '0.85rem', color: 'var(--color-text)', lineHeight: 1.5 }}>
                {steps[step].content}
            </div>
            <div style={{ padding: '0.75rem 1rem', background: 'var(--color-bg)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: '0.25rem' }}>
                    {steps.map((_, i) => (
                        <div key={i} style={{ width: '6px', height: '6px', borderRadius: '50%', background: i === step ? 'var(--color-primary)' : 'var(--color-border)' }} />
                    ))}
                </div>
                <button
                    onClick={nextStep}
                    style={{ background: 'var(--color-primary)', color: 'white', border: 'none', padding: '0.4rem 0.8rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                >
                    {step === steps.length - 1 ? (
                        <>Got it <Check size={14} /></>
                    ) : (
                        <>Next <ChevronRight size={14} /></>
                    )}
                </button>
            </div>
        </div>
    );
}

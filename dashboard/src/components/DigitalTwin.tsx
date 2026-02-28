import { motion } from "framer-motion";

interface DigitalTwinProps {
    riskLevel: 'low' | 'medium' | 'high';
    isSewing: boolean;
}

export function DigitalTwin({ riskLevel, isSewing }: DigitalTwinProps) {
    // Determine posture colors based on risk
    const spineColor = riskLevel === 'high' ? '#ff4d4f' : riskLevel === 'medium' ? '#faad14' : '#52c41a';

    // Animate arms only when actively sewing
    const armRotate = isSewing ? [0, 15, 0, -15, 0] : 0;
    // Hunch the spine forward if the risk is high
    const spineBend = riskLevel === 'high' ? 25 : 0;

    return (
        <div style={{ width: 120, height: 180, position: 'relative', margin: '0 auto' }}>
            <svg viewBox="0 0 100 200" style={{ width: '100%', height: '100%', filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.1))' }}>
                {/* Head */}
                <circle cx="50" cy="30" r="15" fill={spineColor} />

                {/* Torso/Spine */}
                <motion.line
                    x1="50" y1="45"
                    x2="50" y2="120"
                    stroke={spineColor}
                    strokeWidth="12"
                    strokeLinecap="round"
                    animate={{ rotate: spineBend }}
                    style={{ originX: "50px", originY: "120px" }}
                />

                {/* Left Arm */}
                <motion.line
                    x1="38" y1="55"
                    x2="20" y2="100"
                    stroke={spineColor}
                    strokeWidth="8"
                    strokeLinecap="round"
                    animate={{ rotate: armRotate }}
                    transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                    style={{ originX: "38px", originY: "55px" }}
                />

                {/* Right Arm */}
                <motion.line
                    x1="62" y1="55"
                    x2="80" y2="100"
                    stroke={spineColor}
                    strokeWidth="8"
                    strokeLinecap="round"
                    animate={{ rotate: armRotate }}
                    transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                    style={{ originX: "62px", originY: "55px" }}
                />

                {/* Legs Platform (Static to simulate sitting at sewing machine) */}
                <path d="M 50 120 Q 30 180 50 180" stroke="var(--color-text-muted)" strokeWidth="12" fill="none" strokeLinecap="round" />
                <path d="M 50 120 Q 70 180 50 180" stroke="var(--color-text-muted)" strokeWidth="12" fill="none" strokeLinecap="round" />
            </svg>
        </div>
    );
}

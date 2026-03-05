import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useWebSocket } from '../hooks/useWebSocket';
import Header from '../components/Header';
import WorkerCard from '../components/WorkerCard';
import './FloorMap.css';

// Mock static positions for a factory layout if users haven't dragged them yet.
const INITIAL_POSITIONS: Record<string, { x: number, y: number }> = {
    "W02": { x: 20, y: 30 },
    "W03": { x: 40, y: 30 },
    "W04": { x: 60, y: 30 },
    "W05": { x: 80, y: 30 },
    "W06": { x: 20, y: 70 },
    "W07": { x: 40, y: 70 },
    "W08": { x: 60, y: 70 },
};

export default function FloorMap() {
    const { workers } = useWebSocket();
    const [selectedWorkerId, setSelectedWorkerId] = useState<string | null>(null);
    const [positions, setPositions] = useState(INITIAL_POSITIONS);

    const handleDragEnd = (workerId: string, info: any) => {
        // Here we'd ideally save the new X/Y back to a DB, but for now we update local state
        setPositions(prev => ({
            ...prev,
            [workerId]: {
                x: prev[workerId]?.x + (info.offset.x / window.innerWidth) * 100,
                y: prev[workerId]?.y + (info.offset.y / window.innerHeight) * 100
            }
        }));
    };

    const selectedWorker = useMemo(() => {
        return workers.find((w) => w.worker_id === selectedWorkerId) || null;
    }, [workers, selectedWorkerId]);

    return (
        <div className="floor-map-page">
            <Header title="Factory Floor Layout" />

            <div className="layout-container">
                {/* The Map Background area */}
                <div className="map-area">
                    {/* Render a grid pattern mimicking a warehouse floor */}
                    <div className="grid-overlay"></div>

                    {workers.map(w => {
                        const pos = positions[w.worker_id] || { x: 50, y: 50 };

                        // Color code the blips based on state
                        let blipColor = 'var(--color-bg-elevated)';
                        if (w.risk_ergo || w.risk_fatigue) {
                            blipColor = 'var(--color-error)';
                        } else if (w.current_state === 'sewing' || w.current_state === 'adjusting') {
                            blipColor = 'var(--color-success)';
                        } else if (w.current_state === 'break' || w.current_state === 'idle') {
                            blipColor = 'var(--color-warning)';
                        }

                        return (
                            <motion.div
                                key={w.worker_id}
                                className={`worker-blip ${selectedWorkerId === w.worker_id ? 'selected' : ''}`}
                                style={{
                                    left: `${pos.x}%`,
                                    top: `${pos.y}%`,
                                    backgroundColor: blipColor
                                }}
                                drag
                                dragMomentum={false}
                                onDragEnd={(_, info) => handleDragEnd(w.worker_id, info)}
                                onClick={() => setSelectedWorkerId(w.worker_id)}
                                whileHover={{ scale: 1.2 }}
                                whileTap={{ scale: 0.9 }}
                            >
                                <span className="blip-label">{w.name.split(' ')[0]}</span>
                            </motion.div>
                        );
                    })}
                </div>

                {/* Side Panel for clicked worker */}
                {selectedWorker && (
                    <div className="map-side-panel">
                        <h3>Selected Worker</h3>
                        <WorkerCard {...selectedWorker} />
                        <button className="btn btn-secondary" onClick={() => setSelectedWorkerId(null)} style={{ marginTop: '1rem', width: '100%' }}>
                            Close Profile
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

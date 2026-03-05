import { Wifi, WifiOff } from 'lucide-react';

interface ConnectionStatusProps {
    status: 'connected' | 'reconnecting' | 'disconnected';
}

export function ConnectionStatus({ status }: ConnectionStatusProps) {
    if (status === 'connected') {
        return (
            <div className="connection-status" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--color-success)', fontSize: '0.8rem', fontWeight: 500, padding: '0.25rem 0.5rem', backgroundColor: 'var(--color-success-muted)', borderRadius: '999px' }}>
                <Wifi size={14} />
                <span>Live</span>
            </div>
        );
    }

    if (status === 'reconnecting') {
        return (
            <div className="connection-status" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--color-warning)', fontSize: '0.8rem', fontWeight: 500, padding: '0.25rem 0.5rem', backgroundColor: 'var(--color-warning-muted)', borderRadius: '999px' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'currentColor', animation: 'pulse 1.5s infinite' }}></div>
                <span>Reconnecting...</span>
            </div>
        );
    }

    return (
        <div className="connection-status" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--color-error)', fontSize: '0.8rem', fontWeight: 500, padding: '0.25rem 0.5rem', backgroundColor: 'var(--color-error-muted)', borderRadius: '999px' }}>
            <WifiOff size={14} />
            <span>Offline</span>
        </div>
    );
}

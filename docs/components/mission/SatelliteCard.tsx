'use client';

import React from 'react';
import { Satellite } from '@/types/mission';

interface SatelliteCardProps extends Satellite {
  onClick?: () => void;
  isSelected?: boolean;
}

export const SatelliteCard: React.FC<SatelliteCardProps> = ({
  orbitSlot,
  status,
  latency,
  task,
  signal,
  onClick,
  isSelected = false,
}) => {
  const statusConfig = {
    Nominal: { color: 'teal', icon: '🟢', glow: 'glow-teal' },
    Degraded: { color: 'amber', icon: '🟡', glow: 'glow-amber' },
    Critical: { color: 'red', icon: '🔴', glow: 'glow-red' },
  }[status];

  return (
    <div
      className={`group p-4 rounded-xl border-2 bg-black/30 backdrop-blur-sm cursor-pointer transition-all duration-300 hover:scale-105 hover:-translate-y-1 hover:shadow-2xl ${statusConfig.glow} border-${statusConfig.color}-500/30 hover:border-${statusConfig.color}-400 ${
        isSelected ? `ring-4 ring-${statusConfig.color}-500/50 scale-105` : ''
      }`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.();
        }
      }}
      aria-pressed={isSelected}
      aria-label={`Satellite ${orbitSlot} - ${status}`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-mono opacity-75">{orbitSlot}</span>
        <span className={`text-xl`}>{statusConfig.icon}</span>
      </div>
      <div className="text-lg font-bold font-mono text-white mb-1 truncate">
        {status}
      </div>
      <div className="text-xs space-y-1 opacity-75 mb-3">
        <div>{latency}ms | {task}</div>
        <div>Signal: {signal}%</div>
      </div>
      <div className="w-full bg-black/50 rounded-full h-2 overflow-hidden">
        <div
          className={`bg-gradient-to-r from-${statusConfig.color}-400 to-${statusConfig.color}-600 h-2 rounded-full transition-all`}
          style={{ width: `${Math.min(signal, 100)}%` }}
          role="progressbar"
          aria-valuenow={signal}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
};

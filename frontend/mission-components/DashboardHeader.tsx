'use client';

import React, { useState, useEffect } from 'react';
import { MissionState } from '@/types/dashboard';

interface DashboardHeaderProps {
  data: MissionState;
}

const statusIcon = (status: MissionState['status']): string => {
  const icons: Record<MissionState['status'], string> = {
    Nominal: '🟢',
    Degraded: '🟡',
    Critical: '🔴',
  };
  return icons[status];
};

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({ data }) => {
  const [time, setTime] = useState<string>('');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Initialize time on mount
    const updateTime = () => {
      const now = new Date();
      setTime(
        now.toLocaleTimeString('en-IN', {
          hour: '2-digit',
          minute: '2-digit',
          timeZone: 'Asia/Kolkata',
          hour12: true,
        })
      );
    };

    updateTime();
    setMounted(true);

    // Update every 30 seconds for demo performance
    const interval = setInterval(updateTime, 30000);
    return () => clearInterval(interval);
  }, []);

  if (!mounted) {
    return (
      <header className="h-20 bg-black/80 backdrop-blur-md border-b border-teal-500/30 flex items-center px-6 fixed w-full z-50">
        <div className="opacity-0">Loading...</div>
      </header>
    );
  }

  return (
    <header className="h-20 bg-black/80 backdrop-blur-md border-b border-teal-500/30 flex items-center px-6 fixed w-full z-50 shadow-lg shadow-teal-500/20">
      <div className="flex items-center space-x-4 w-full">
        {/* Logo */}
        <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-teal-500 to-cyan-500 rounded-lg glow-teal animate-pulse flex items-center justify-center font-bold text-black">
          AG
        </div>

        {/* Mission Info */}
        <div className="flex-1">
          <h1 className="text-2xl font-bold font-mono text-white tracking-tight">
            {data.name}
          </h1>
          <div className="flex items-center space-x-3 text-sm text-gray-300">
            <span className="px-3 py-1 bg-gray-900/50 rounded-full text-teal-400 border border-teal-500/30 font-mono">
              {data.phase}
            </span>
            <span className="text-xl">{statusIcon(data.status)}</span>
            <span className="font-mono">{time}</span>
            {data.anomalyCount > 0 && (
              <span className="bg-red-500/20 text-red-400 px-2 py-1 rounded-full text-xs font-mono animate-pulse border border-red-500/50">
                {data.anomalyCount} Alert{data.anomalyCount > 1 ? 's' : ''}
              </span>
            )}
          </div>
        </div>

        {/* Status Badge */}
        <div className="hidden sm:flex items-center space-x-2 text-right">
          <div className="text-right">
            <p className="text-xs text-gray-400">Status</p>
            <p className="text-lg font-bold text-teal-400">{data.status}</p>
          </div>
          <div
            className={`w-3 h-3 rounded-full animate-pulse ${
              data.status === 'Nominal'
                ? 'bg-green-500'
                : data.status === 'Degraded'
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
            }`}
          />
        </div>
      </div>
    </header>
  );
};

'use client';

import React from 'react';
import { MissionPhase } from '@/types/mission';

interface PhaseTimelineProps {
  phases: MissionPhase[];
}

export const PhaseTimeline: React.FC<PhaseTimelineProps> = ({ phases }) => {
  const activeIndex = phases.findIndex((p) => p.isActive);

  return (
    <div className="space-y-6">
      <h3 className="text-2xl font-bold text-teal-400 mb-6 glow-teal flex items-center gap-2">
        <span>🚀</span> Mission Timeline
      </h3>

      {/* Main Timeline Bar */}
      <div className="space-y-4">
        {/* Gradient Fill Bar */}
        <div className="relative">
          <div className="flex items-center w-full h-4 bg-black/50 rounded-full border border-teal-500/30">
            {phases.map((phase, i) => (
              <div
                key={phase.name}
                className={`h-4 transition-all ${
                  i <= activeIndex
                    ? 'bg-gradient-to-r from-teal-400 to-cyan-500 glow-teal shadow-lg'
                    : 'bg-gray-800/50'
                }`}
                style={{ width: `${100 / phases.length}%` }}
                role="progressbar"
                aria-valuenow={i <= activeIndex ? 100 : 0}
                aria-valuemin={0}
                aria-valuemax={100}
              />
            ))}
          </div>

          {/* Active Phase Label */}
          {phases[activeIndex] && (
            <div className="absolute -bottom-12 left-0 right-0">
              <div className="inline-block bg-black/90 backdrop-blur-sm p-3 rounded-lg border border-teal-500/50 glow-teal">
                <div className="text-xs font-mono opacity-75 mb-1 uppercase tracking-wider">
                  {phases[activeIndex].name}
                </div>
                <div className="text-lg font-bold text-teal-400 font-mono">
                  {phases[activeIndex].progress}% • {phases[activeIndex].eta}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Phase List Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 mt-12 pt-6 border-t border-gray-700">
          {phases.map((phase) => (
            <div
              key={phase.name}
              className={`p-3 rounded-lg text-center text-xs transition-all ${
                phase.isActive
                  ? 'bg-teal-500/20 border-2 border-teal-400 glow-teal font-bold text-teal-300'
                  : 'bg-gray-900/50 border border-gray-700 text-gray-400 hover:bg-gray-800'
              }`}
              role="status"
              aria-current={phase.isActive ? 'step' : undefined}
            >
              <div className="font-mono text-xs uppercase mb-1 tracking-wider">
                {phase.name.split(' ')[0]}
              </div>
              <div className="text-base font-bold">{phase.progress}%</div>
              <div className="text-xs opacity-75 mt-1">{phase.eta}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

'use client';

import React, { useState, useEffect } from 'react';
import { Satellite, MissionPhase } from '@/types/mission';
import missionData from '@/public/mocks/mission.json';
import { SatelliteCard } from './SatelliteCard';
import { PhaseTimeline } from './PhaseTimeline';

const TASK_ROTATION = ['Data Dump', 'Imaging', 'Orbit Adjust', 'Telemetry', 'Standby', 'Calibration'];

export const MissionPanel: React.FC = () => {
  const [satellites, setSatellites] = useState<Satellite[]>(
    (missionData.satellites as unknown as Satellite[])
  );
  const [phases, setPhases] = useState<MissionPhase[]>(
    (missionData.phases as unknown as MissionPhase[])
  );
  const [selectedSat, setSelectedSat] = useState<Satellite | null>(null);
  const [taskIndex, setTaskIndex] = useState(0);

  // 10s demo cycle: rotate tasks and advance phases
  useEffect(() => {
    const interval = setInterval(() => {
      // Rotate tasks
      setTaskIndex((prev) => (prev + 1) % TASK_ROTATION.length);

      setSatellites((prev) =>
        prev.map((sat, idx) => ({
          ...sat,
          task: TASK_ROTATION[(idx + taskIndex) % TASK_ROTATION.length],
          latency: Math.max(20, sat.latency + (Math.random() - 0.5) * 30),
          signal: Math.max(0, Math.min(100, sat.signal + (Math.random() - 0.5) * 10)),
        }))
      );

      // Advance active phase
      setPhases((prev) => {
        const activeIdx = prev.findIndex((p) => p.isActive);
        const nextIdx = (activeIdx + 1) % prev.length;

        return prev.map((phase, i) => ({
          ...phase,
          isActive: i === nextIdx,
          progress:
            i === nextIdx
              ? Math.min(100, phase.progress + 5)
              : i < nextIdx
                ? 100
                : 0,
        }));
      });
    }, 10000);

    return () => clearInterval(interval);
  }, [taskIndex]);

  const nominalCount = satellites.filter((s) => s.status === 'Nominal').length;

  return (
    <div className="space-y-12 w-full pb-8">
      {/* Satellite Tracker Section */}
      <section className="space-y-6">
        <div className="flex items-center gap-3">
          <h2 className="text-3xl font-bold text-teal-400 glow-teal">🛰️ Satellite Tracker</h2>
          <div className="px-3 py-1 rounded-full bg-teal-500/20 border border-teal-500/50 text-teal-300 text-sm font-mono">
            {nominalCount}/6 Nominal
          </div>
        </div>

        {/* Responsive Satellite Grid: 6→3→2→1 columns */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 auto-rows-max">
          {satellites.map((sat) => (
            <SatelliteCard
              key={sat.id}
              {...sat}
              isSelected={selectedSat?.id === sat.id}
              onClick={() => setSelectedSat(sat)}
            />
          ))}
        </div>
      </section>

      {/* Selected Satellite Details */}
      {selectedSat && (
        <section
          className="p-6 bg-black/50 backdrop-blur-xl rounded-2xl border-2 border-teal-500/30 glow-teal/50 animate-fadeIn"
          role="region"
          aria-label="Selected satellite details"
        >
          <h3 className="text-xl font-bold text-teal-400 mb-4 glow-teal">
            🔍 Selected: {selectedSat.orbitSlot}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="p-3 bg-teal-500/10 rounded-lg border border-teal-500/20">
              <span className="opacity-75 block text-xs uppercase tracking-widest mb-1">Status</span>
              <span className="font-mono text-lg text-teal-300">{selectedSat.status}</span>
            </div>
            <div className="p-3 bg-teal-500/10 rounded-lg border border-teal-500/20">
              <span className="opacity-75 block text-xs uppercase tracking-widest mb-1">Latency</span>
              <span className="font-mono text-lg text-teal-300">{selectedSat.latency.toFixed(0)}ms</span>
            </div>
            <div className="p-3 bg-teal-500/10 rounded-lg border border-teal-500/20">
              <span className="opacity-75 block text-xs uppercase tracking-widest mb-1">Current Task</span>
              <span className="font-mono text-lg text-teal-300">{selectedSat.task}</span>
            </div>
            <div className="p-3 bg-teal-500/10 rounded-lg border border-teal-500/20">
              <span className="opacity-75 block text-xs uppercase tracking-widest mb-1">Signal</span>
              <span className="font-mono text-lg text-teal-300">{selectedSat.signal.toFixed(0)}%</span>
            </div>
          </div>
        </section>
      )}

      {/* Mission Phase Timeline */}
      <section className="pt-6 border-t border-gray-700">
        <PhaseTimeline phases={phases} />
      </section>

      {/* Auto-scroll trigger on tab change */}
      <script
        dangerouslySetInnerHTML={{
          __html: `
            if (typeof window !== 'undefined') {
              const observer = new MutationObserver(() => {
                const missionPanel = document.querySelector('[role="tabpanel"]');
                if (missionPanel) {
                  missionPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
              });
              observer.observe(document.body, { subtree: true, childList: true });
            }
          `,
        }}
      />
    </div>
  );
};

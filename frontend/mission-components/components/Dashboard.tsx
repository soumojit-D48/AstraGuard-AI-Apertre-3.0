'use client';

import React, { useState, useEffect } from 'react';
import { DashboardHeader } from './DashboardHeader';
import { VerticalNav } from './VerticalNav';
import { MissionPanel } from '@/components/mission/MissionPanel';
import { MissionState, TabType } from '@/types/dashboard';
import dashboardMocks from '@/public/mocks/dashboard.json';

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('mission');
  const [mission, setMission] = useState<MissionState>(dashboardMocks.mission as MissionState);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);

    // Update timestamp every 30 seconds
    const interval = setInterval(() => {
      const now = new Date();
      const newTime = now.toLocaleTimeString('en-IN', {
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'Asia/Kolkata',
        hour12: true,
      });
      setMission((prev) => ({ ...prev, updated: newTime }));
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
  };

  const handleKeyDown = (e: React.KeyboardEvent, tab: TabType) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleTabChange(tab);
    }
  };

  if (!mounted) {
    return (
      <div className="dashboard-container min-h-screen text-white font-mono antialiased flex items-center justify-center">
        <div className="text-center">
          <p className="text-teal-400 text-xl">Loading Mission Control...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container min-h-screen text-white font-mono antialiased">
      {/* Header */}
      <DashboardHeader data={mission} />

      {/* Main Layout */}
      <div className="flex pt-20">
        {/* Navigation Sidebar */}
        <VerticalNav />

        {/* Main Content Area */}
        <main className="flex-1 overflow-auto">
          {/* Tab Navigation Bar */}
          <div className="sticky top-0 z-10 bg-black/80 backdrop-blur-md border-b border-teal-500/30 px-6">
            <nav
              role="tablist"
              aria-label="Mission Control Tabs"
              className="flex space-x-8 py-4"
            >
              {/* Mission Tab */}
              <button
                role="tab"
                aria-selected={activeTab === 'mission'}
                aria-controls="mission-panel"
                id="mission-tab"
                className={`px-6 py-3 rounded-t-xl font-mono text-lg font-semibold transition-all duration-300 focus-visible:outline-offset-2 ${
                  activeTab === 'mission'
                    ? 'tab-active-teal bg-teal-500/10 border-b-2'
                    : 'text-gray-400 hover:text-teal-300 hover:bg-teal-500/5 border-b-2 border-transparent'
                }`}
                onClick={() => handleTabChange('mission')}
                onKeyDown={(e) => handleKeyDown(e, 'mission')}
              >
                Mission Control
              </button>

              {/* Systems Tab */}
              <button
                role="tab"
                aria-selected={activeTab === 'systems'}
                aria-controls="systems-panel"
                id="systems-tab"
                className={`px-6 py-3 rounded-t-xl font-mono text-lg font-semibold transition-all duration-300 focus-visible:outline-offset-2 ${
                  activeTab === 'systems'
                    ? 'tab-active-magenta bg-magenta-500/10 border-b-2'
                    : 'text-gray-400 hover:text-magenta-300 hover:bg-magenta-500/5 border-b-2 border-transparent'
                }`}
                onClick={() => handleTabChange('systems')}
                onKeyDown={(e) => handleKeyDown(e, 'systems')}
              >
                Systems Health
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-8 min-h-[calc(100vh-240px)]">
            {/* Mission Panel */}
            <section
              id="mission-panel"
              role="tabpanel"
              aria-labelledby="mission-tab"
              aria-hidden={activeTab !== 'mission'}
              className={`transition-all duration-500 transform ${
                activeTab === 'mission'
                  ? 'scale-100 opacity-100'
                  : 'scale-95 opacity-0 pointer-events-none'
              }`}
            >
              <MissionPanel />
            </section>

            {/* Systems Panel */}
            <section
              id="systems-panel"
              role="tabpanel"
              aria-labelledby="systems-tab"
              aria-hidden={activeTab !== 'systems'}
              className={`transition-all duration-500 transform ${
                activeTab === 'systems'
                  ? 'scale-100 opacity-100'
                  : 'scale-95 opacity-0 pointer-events-none'
              }`}
            >
              <div className="p-12 rounded-2xl border-2 border-magenta-500/50 bg-gradient-to-br from-magenta-500/10 via-transparent to-purple-500/5 backdrop-blur-sm">
                <div className="text-center py-20">
                  <h2 className="text-5xl font-bold mb-4 text-magenta-400 glow-magenta">
                    Systems Health
                  </h2>
                  <p className="text-xl text-gray-300 mb-6 font-mono">
                    Ready for KPIs, breakers, and telemetry charts
                  </p>
                  <div className="inline-block px-6 py-3 rounded-lg bg-magenta-500/20 border border-magenta-500/50 text-magenta-300 text-sm font-mono">
                    📊 Issue #89 Foundation
                  </div>
                </div>

                {/* Systems Placeholder */}
                <div className="mt-12 space-y-4">
                  {['Power Systems', 'Thermal Control', 'Communications', 'Attitude Control'].map(
                    (system, idx) => (
                      <div
                        key={idx}
                        className="p-4 rounded-lg bg-black/50 border border-magenta-500/30 hover:border-magenta-500/60 transition-colors flex items-center justify-between group"
                      >
                        <span className="text-magenta-300 font-mono">{system}</span>
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse group-hover:glow-teal" />
                      </div>
                    )
                  )}
                </div>
              </div>
            </section>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;

'use client';

import React, { useState } from 'react';
import { NavItem } from '@/types/dashboard';

const NAV_ITEMS: NavItem[] = [
  { icon: '🛰️', label: 'Orbit View', href: '/orbit' },
  { icon: '📡', label: 'Telemetry', href: '/telemetry' },
  { icon: '📋', label: 'Logs', href: '/logs' },
  { icon: '⚙️', label: 'Settings', href: '/settings' },
];

export const VerticalNav: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const handleNavClick = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsOpen(false);
  };

  return (
    <>
      {/* Mobile Hamburger Button */}
      <button
        className="md:hidden fixed top-24 left-4 z-40 p-2 rounded-lg bg-black/50 border border-teal-500/50 glow-teal hover:bg-teal-500/20 transition-colors"
        onClick={() => setIsOpen(true)}
        aria-label="Open navigation menu"
        aria-expanded={isOpen}
        aria-controls="nav-drawer"
      >
        <svg
          className="w-6 h-6 text-teal-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>

      {/* Navigation Drawer - Desktop Sidebar + Mobile Drawer */}
      <aside
        id="nav-drawer"
        className={`fixed md:static md:translate-x-0 inset-y-0 left-0 w-80 bg-black/95 backdrop-blur-xl border-r border-teal-500/30 z-30 transform transition-transform duration-300 ease-out md:ease-none ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        role="navigation"
        aria-label="Main navigation"
      >
        {/* Nav Header */}
        <div className="h-20 flex items-center px-6 border-b border-teal-500/20 bg-black/50 backdrop-blur">
          <h2 className="text-xl font-bold text-teal-400 font-mono tracking-wider">
            Navigation
          </h2>
          <button
            className="md:hidden ml-auto p-2 hover:bg-teal-500/10 rounded-lg transition-colors"
            onClick={() => setIsOpen(false)}
            aria-label="Close navigation menu"
          >
            <svg
              className="w-6 h-6 text-teal-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Nav Items */}
        <nav className="p-4 space-y-2 overflow-y-auto">
          {NAV_ITEMS.map((item) => (
            <a
              key={item.href}
              href={item.href}
              onClick={handleNavClick}
              className="flex items-center space-x-3 px-4 py-3 rounded-xl text-gray-300 hover:bg-teal-500/10 hover:text-teal-400 hover:border hover:border-teal-500/30 transition-all duration-200 group focus-visible:outline-teal-500 focus-visible:outline-offset-2"
              role="menuitem"
            >
              <span className="text-2xl group-hover:scale-110 transition-transform">
                {item.icon}
              </span>
              <span className="font-mono text-sm font-semibold group-hover:translate-x-1 transition-transform">
                {item.label}
              </span>
            </a>
          ))}
        </nav>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Footer Info */}
        <div className="p-4 border-t border-teal-500/20 text-xs text-gray-400 font-mono">
          <p>Mission Control v1.0</p>
          <p className="mt-1 text-teal-400">ECWoC26</p>
        </div>
      </aside>

      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 md:hidden transition-opacity"
          onClick={() => setIsOpen(false)}
          role="presentation"
          aria-hidden="true"
        />
      )}
    </>
  );
};

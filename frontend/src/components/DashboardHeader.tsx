'use client';

import NotificationBell from './notifications/NotificationBell';

interface DashboardHeaderProps {
  title: string;
  subtitle?: string;
}

export default function DashboardHeader({ title, subtitle }: DashboardHeaderProps) {
  return (
    <header className="flex items-center justify-between mb-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
        {subtitle && (
          <p className="text-gray-600 mt-1">{subtitle}</p>
        )}
      </div>
      <div className="flex items-center gap-4">
        <NotificationBell />
      </div>
    </header>
  );
}

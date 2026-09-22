import React from 'react';
import { Card, CardBody } from './Card';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ReactNode;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  trend = 'neutral',
  icon
}) => {
  const trendColors = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-gray-600'
  };

  return (
    <Card>
      <CardBody>
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {change && (
              <p className={`text-sm mt-1 ${trendColors[trend]}`}>
                {change}
              </p>
            )}
          </div>
          {icon && (
            <div className="p-2 bg-gray-100 rounded-lg">
              {icon}
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
};

// Simplified dashboard grid for reduced cognitive load
export const DashboardGrid: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    {children}
  </div>
);

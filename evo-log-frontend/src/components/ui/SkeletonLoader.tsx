import React from 'react';

interface SkeletonProps {
  className?: string;
  type?: 'text' | 'circular' | 'rectangular';
}

export function Skeleton({ className = '', type = 'text' }: SkeletonProps) {
  const baseClasses = 'animate-pulse bg-outline-variant/30';
  
  let shapeClasses = 'rounded';
  if (type === 'circular') {
    shapeClasses = 'rounded-full';
  } else if (type === 'rectangular') {
    shapeClasses = 'rounded-lg';
  }

  return (
    <div className={`${baseClasses} ${shapeClasses} ${className}`} />
  );
}

export function TableSkeleton({ rows = 5, columns = 5 }) {
  return (
    <div className="w-full">
      <div className="flex border-b border-outline-variant py-3">
        {Array.from({ length: columns }).map((_, i) => (
          <div key={i} className="flex-1 px-4">
            <Skeleton type="text" className="h-4 w-3/4" />
          </div>
        ))}
      </div>
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex border-b border-outline-variant py-4">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <div key={colIndex} className="flex-1 px-4">
              <Skeleton type="text" className="h-3 w-full" />
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="p-4 border border-outline-variant rounded-xl flex flex-col gap-4">
      <div className="flex justify-between items-start">
        <Skeleton type="circular" className="h-10 w-10" />
        <Skeleton type="text" className="h-4 w-16" />
      </div>
      <div className="space-y-2">
        <Skeleton type="text" className="h-3 w-1/2" />
        <Skeleton type="text" className="h-6 w-1/4" />
      </div>
      <div className="mt-4 pt-4 border-t border-outline-variant">
        <Skeleton type="text" className="h-3 w-3/4" />
      </div>
    </div>
  );
}

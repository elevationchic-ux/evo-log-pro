import React from 'react'

interface MaterialSymbolProps {
  icon: string
  size?: number
  className?: string
}

export function MaterialSymbol({ icon, size = 24, className = '' }: MaterialSymbolProps) {
  return (
    <span 
      className="material-symbols-outlined"
      style={{ fontSize: size }}
    >
      {icon}
    </span>
  )
}

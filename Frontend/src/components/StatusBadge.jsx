import React from 'react';

export function StatusBadge({ verdict, size = 'md' }) {
  const v = (verdict || 'Unverifiable').toLowerCase();
  
  let bgColor = 'bg-slate-600';
  let label = verdict || 'Unverifiable';

  if (v === 'true') {
    bgColor = 'bg-emerald-700';
    label = 'Verified True';
  } else if (v === 'false') {
    bgColor = 'bg-rose-700';
    label = 'Verified False';
  } else if (v === 'misleading') {
    bgColor = 'bg-amber-700';
    label = 'Misleading / Distorted';
  } else if (v === 'unverifiable') {
    bgColor = 'bg-slate-600';
    label = 'Unverifiable Guardrail';
  }

  const sizeClass = size === 'sm' 
    ? 'text-xs px-2.5 py-0.5' 
    : size === 'lg' 
      ? 'text-sm px-4 py-1.5 font-bold tracking-wide' 
      : 'text-xs px-3 py-1 font-semibold';

  return (
    <span className={`inline-flex items-center rounded-sm text-white uppercase tracking-wider ${bgColor} ${sizeClass}`}>
      {label}
    </span>
  );
}

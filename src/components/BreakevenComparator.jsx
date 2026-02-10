import React from 'react';
import { formatINRLakhs } from '../utils/formatters';

const BreakevenComparator = ({ weeklyMetrics }) => {
  return (
    <div className="bg-slate-800 p-4 rounded-lg mb-6 hover:bg-slate-750 transition-colors">
      <h3 className="text-lg font-semibold mb-4">Breakeven Comparator</h3>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-slate-700/50 p-3 rounded">
          <p className="text-sm text-slate-400 mb-1">Hybrid Model (Current)</p>
          <p className="text-xl font-semibold">{formatINRLakhs(weeklyMetrics.hybridCost)}</p>
        </div>
        <div className="bg-slate-700/50 p-3 rounded">
          <p className="text-sm text-slate-400 mb-1">100% Gig Model</p>
          <p className="text-xl font-semibold">{formatINRLakhs(weeklyMetrics.gigOnlyCost)}</p>
        </div>
      </div>
      <div className={`p-3 rounded ${weeklyMetrics.isSaving ? 'bg-green-900/30' : 'bg-red-900/30'}`}>
        <p className={`text-lg font-bold ${weeklyMetrics.isSaving ? 'text-green-400' : 'text-red-400'}`}>
          {weeklyMetrics.isSaving ? '✓ ' : '✗ '}
          {weeklyMetrics.isSaving ? 'Hybrid Model saves ' : 'Hybrid Model loses '}
          {formatINRLakhs(Math.abs(weeklyMetrics.costDelta))}/week
        </p>
        {!weeklyMetrics.isSaving && (
          <p className="text-xs text-red-300 mt-1">
            Too much idle time detected
          </p>
        )}
      </div>
    </div>
  );
};

export default BreakevenComparator;

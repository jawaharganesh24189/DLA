import React from 'react';
import { Bike, DollarSign, AlertTriangle } from 'lucide-react';
import { formatINR, formatPercentage } from '../utils/formatters';

const KPICards = ({ weeklyMetrics }) => {
  return (
    <div className="grid grid-cols-2 gap-4 mb-6">
      <div className="bg-slate-800 p-4 rounded-lg hover:bg-slate-750 transition-colors">
        <div className="flex items-center mb-2">
          <Bike className="w-5 h-5 text-swiggy-orange mr-2" />
          <h3 className="text-sm text-slate-400">Fleet Utilization Rate</h3>
        </div>
        <p className={`text-2xl font-bold ${weeklyMetrics.avgUtilization < 70 ? 'text-red-500' : 'text-green-500'}`}>
          {formatPercentage(weeklyMetrics.avgUtilization)}
        </p>
        {weeklyMetrics.avgUtilization < 70 && (
          <p className="text-xs text-red-400 mt-1 flex items-center">
            <AlertTriangle className="w-3 h-3 mr-1" />
            Overstaffed
          </p>
        )}
      </div>
      
      <div className="bg-slate-800 p-4 rounded-lg hover:bg-slate-750 transition-colors">
        <div className="flex items-center mb-2">
          <DollarSign className="w-5 h-5 text-swiggy-orange mr-2" />
          <h3 className="text-sm text-slate-400">Avg Cost Per Order</h3>
        </div>
        <p className="text-2xl font-bold">
          {formatINR(weeklyMetrics.avgCostPerOrder.toFixed(2))}
        </p>
      </div>
    </div>
  );
};

export default KPICards;

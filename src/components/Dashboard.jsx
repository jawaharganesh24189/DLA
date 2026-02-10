import React, { useState, useRef } from 'react';
import { Download } from 'lucide-react';
import Slider from './Slider';
import KPICards from './KPICards';
import BreakevenComparator from './BreakevenComparator';
import UtilizationChart from './UtilizationChart';
import ContributionMarginCalculator from './ContributionMarginCalculator';
import { exportToCSV } from '../utils/exportData';

const Dashboard = ({ 
  fleetSize, 
  targetUtilization, 
  onFleetSizeChange, 
  onUtilizationChange,
  weeklyMetrics,
  chartData,
  simulationResults
}) => {
  const [showContributionCalc, setShowContributionCalc] = useState(false);

  const handleExportData = () => {
    exportToCSV(simulationResults, weeklyMetrics);
  };

  return (
    <div className="w-1/2 overflow-y-auto p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">Simulation Dashboard</h2>
          <button
            onClick={handleExportData}
            className="flex items-center gap-2 px-4 py-2 bg-swiggy-orange text-white rounded-lg hover:bg-orange-600 transition-colors"
          >
            <Download className="w-4 h-4" />
            Export Data
          </button>
        </div>
        
        {/* User Input Sliders */}
        <div className="bg-slate-800 p-4 rounded-lg mb-6">
          <Slider
            label="Permanent Fleet Size"
            value={fleetSize}
            min={0}
            max={1000}
            step={10}
            onChange={onFleetSizeChange}
            unit=" riders"
          />
          <Slider
            label="Target Utilization"
            value={targetUtilization}
            min={50}
            max={100}
            step={5}
            onChange={onUtilizationChange}
            unit="%"
          />
        </div>
        
        {/* KPI Cards */}
        <KPICards weeklyMetrics={weeklyMetrics} />
        
        {/* Breakeven Comparator */}
        <BreakevenComparator weeklyMetrics={weeklyMetrics} />
        
        {/* Contribution Margin Calculator Toggle */}
        <div className="mb-6">
          <button
            onClick={() => setShowContributionCalc(!showContributionCalc)}
            className="w-full py-2 px-4 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors"
          >
            {showContributionCalc ? '− Hide' : '+ Show'} Contribution Margin Calculator
          </button>
        </div>

        {showContributionCalc && (
          <ContributionMarginCalculator weeklyMetrics={weeklyMetrics} />
        )}
        
        {/* Utilization Trap Chart */}
        <UtilizationChart chartData={chartData} />
      </div>
    </div>
  );
};

export default Dashboard;

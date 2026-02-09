import React, { useState, useMemo } from 'react';
import { 
  ComposedChart, 
  Bar, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  ReferenceArea
} from 'recharts';
import { Bike, TrendingUp, AlertTriangle, DollarSign } from 'lucide-react';

// Utility function to format Indian currency
const formatINR = (amount) => {
  return `₹${amount.toLocaleString('en-IN')}`;
};

const formatINRLakhs = (amount) => {
  const lakhs = amount / 100000;
  return `₹${lakhs.toFixed(2)} L`;
};

const SwiggyFleetSimulator = () => {
  // Default configuration state
  const [config, setConfig] = useState({
    // Unit Economics
    aov: 400,
    commissionRate: 22,
    deliveryFee: 30,
    
    // Permanent Fleet
    monthlySalary: 22000,
    dailyAllowance: 150,
    monthlyInsurance: 2000,
    shiftHours: 10,
    maxOrdersPerDay: 22,
    
    // Gig Fleet
    basePayoutPerOrder: 45,
    surgeMultiplier: 1.6,
    gigAvailabilityCap: 5000,
    
    // Demand Scenario
    demandScenario: [
      { day: 'Monday', orders: 8500 },
      { day: 'Tuesday', orders: 8500 },
      { day: 'Wednesday', orders: 8500 },
      { day: 'Thursday', orders: 8500 },
      { day: 'Friday', orders: 11000 },
      { day: 'Saturday', orders: 14500 },
      { day: 'Sunday', orders: 14500 },
    ],
  });
  
  // User inputs - the levers
  const [fleetSize, setFleetSize] = useState(400);
  const [targetUtilization, setTargetUtilization] = useState(85);
  
  // Handle config field changes
  const handleConfigChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: parseFloat(value) || 0
    }));
  };
  
  // Handle demand scenario changes
  const handleDemandChange = (index, value) => {
    setConfig(prev => ({
      ...prev,
      demandScenario: prev.demandScenario.map((item, i) => 
        i === index ? { ...item, orders: parseFloat(value) || 0 } : item
      )
    }));
  };
  
  // Calculate daily fixed cost per rider
  const dailyFixedCost = useMemo(() => {
    return ((config.monthlySalary + config.monthlyInsurance) / 30) + config.dailyAllowance;
  }, [config.monthlySalary, config.monthlyInsurance, config.dailyAllowance]);
  
  // Main simulation calculations
  const simulationResults = useMemo(() => {
    const results = config.demandScenario.map(({ day, orders: projectedOrders }) => {
      // 1. Permanent Capacity
      const permCapacity = Math.floor(fleetSize * config.maxOrdersPerDay * (targetUtilization / 100));
      
      // 2. Gig Orders Needed
      const gigOrdersNeeded = Math.max(0, projectedOrders - permCapacity);
      
      // 3. Utilization Analysis
      let idleCount = 0;
      let wasteCost = 0;
      let isOverCapacity = false;
      
      if (permCapacity > projectedOrders) {
        idleCount = permCapacity - projectedOrders;
        wasteCost = (idleCount / config.maxOrdersPerDay) * dailyFixedCost;
        isOverCapacity = true;
      }
      
      // 4. Cost Calculations
      const fixedFleetCost = fleetSize * dailyFixedCost;
      
      // Apply surge if gig orders exceed 30% of total demand
      const isSurge = gigOrdersNeeded > (projectedOrders * 0.3);
      const gigPayoutRate = isSurge ? 
        config.basePayoutPerOrder * config.surgeMultiplier : 
        config.basePayoutPerOrder;
      
      const gigFleetCost = gigOrdersNeeded * gigPayoutRate;
      
      // 5. Profitability
      const revenuePerOrder = (config.aov * (config.commissionRate / 100)) + config.deliveryFee;
      const totalRevenue = projectedOrders * revenuePerOrder;
      const totalCost = fixedFleetCost + gigFleetCost;
      const netMargin = totalRevenue - totalCost;
      
      // Calculate actual utilization
      const actualUtilization = permCapacity > 0 ? 
        Math.min(100, (projectedOrders / permCapacity) * 100) : 
        0;
      
      return {
        day,
        projectedOrders,
        permCapacity,
        gigOrdersNeeded,
        idleCount,
        wasteCost,
        isOverCapacity,
        isSurge,
        fixedFleetCost,
        gigFleetCost,
        totalRevenue,
        totalCost,
        netMargin,
        actualUtilization,
      };
    });
    
    return results;
  }, [config, fleetSize, targetUtilization, dailyFixedCost]);
  
  // Calculate 100% Gig scenario for comparison
  const gigOnlyScenario = useMemo(() => {
    let totalCost = 0;
    let totalRevenue = 0;
    
    config.demandScenario.forEach(({ orders }) => {
      const revenuePerOrder = (config.aov * (config.commissionRate / 100)) + config.deliveryFee;
      totalRevenue += orders * revenuePerOrder;
      totalCost += orders * config.basePayoutPerOrder;
    });
    
    return {
      totalCost,
      totalRevenue,
      netMargin: totalRevenue - totalCost,
    };
  }, [config]);
  
  // Calculate aggregate metrics
  const weeklyMetrics = useMemo(() => {
    const totalOrders = simulationResults.reduce((sum, day) => sum + day.projectedOrders, 0);
    const totalCost = simulationResults.reduce((sum, day) => sum + day.totalCost, 0);
    const totalRevenue = simulationResults.reduce((sum, day) => sum + day.totalRevenue, 0);
    const totalNetMargin = simulationResults.reduce((sum, day) => sum + day.netMargin, 0);
    const avgUtilization = simulationResults.reduce((sum, day) => sum + day.actualUtilization, 0) / simulationResults.length;
    
    const avgCostPerOrder = totalOrders > 0 ? totalCost / totalOrders : 0;
    
    const hybridCost = totalCost;
    const gigOnlyCost = gigOnlyScenario.totalCost;
    const costDelta = gigOnlyCost - hybridCost;
    const isSaving = costDelta > 0;
    
    return {
      totalOrders,
      totalCost,
      totalRevenue,
      totalNetMargin,
      avgUtilization,
      avgCostPerOrder,
      hybridCost,
      gigOnlyCost,
      costDelta,
      isSaving,
    };
  }, [simulationResults, gigOnlyScenario]);
  
  // Prepare chart data
  const chartData = simulationResults.map(result => ({
    day: result.day.substring(0, 3),
    permCapacity: result.permCapacity,
    gigOrders: result.gigOrdersNeeded,
    demand: result.projectedOrders,
    isOverCapacity: result.isOverCapacity,
  }));
  
  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <div className="flex h-screen">
        {/* LEFT PANEL - Admin/Config Panel */}
        <div className="w-1/2 overflow-y-auto border-r border-slate-700 p-6">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-swiggy-orange mb-2">
              Swiggy Fleet Strategy Simulator
            </h1>
            <p className="text-slate-400 text-sm">
              Configure parameters and analyze the financial impact of fleet composition
            </p>
          </div>
          
          {/* Unit Economics Section */}
          <div className="mb-6 bg-slate-800 p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-3 text-swiggy-orange flex items-center">
              <DollarSign className="w-5 h-5 mr-2" />
              Unit Economics (Revenue)
            </h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-slate-300 mb-1">
                  Avg Order Value (AOV)
                </label>
                <input
                  type="number"
                  value={config.aov}
                  onChange={(e) => handleConfigChange('aov', e.target.value)}
                  className="w-full bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-swiggy-orange focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">
                  Commission Rate (%)
                </label>
                <input
                  type="number"
                  value={config.commissionRate}
                  onChange={(e) => handleConfigChange('commissionRate', e.target.value)}
                  className="w-full bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-swiggy-orange focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">
                  Customer Delivery Fee
                </label>
                <input
                  type="number"
                  value={config.deliveryFee}
                  onChange={(e) => handleConfigChange('deliveryFee', e.target.value)}
                  className="w-full bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-swiggy-orange focus:outline-none"
                />
              </div>
            </div>
          </div>
          
          {/* Permanent Fleet Section */}
          <div className="mb-6 bg-slate-800 p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-3 text-swiggy-orange flex items-center">
              <Bike className="w-5 h-5 mr-2" />
              Permanent Fleet (Fixed Cost Model)
            </h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-slate-300 mb-1">
                  Monthly Salary (CTC)
                </label>
                <input
                  type="number"
                  value={config.monthlySalary}
                  onChange={(e) => handleConfigChange('monthlySalary', e.target.value)}
                  className="w-full bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-swiggy-orange focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">
                  Daily Fuel/Maintenance Allowance
                </label>
                <input
                  type="number"
                  value={config.dailyAllowance}
                  onChange={(e) => handleConfigChange('dailyAllowance', e.target.value)}
                  className="w-full bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-swiggy-orange focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">
                  Insurance/Benefits per Rider (Monthly)
                </label>
                <input
                  type="number"
                  value={config.monthlyInsurance}
                  onChange={(e) => handleConfigChange('monthlyInsurance', e.target.value)}
                  className="w-full bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-swiggy-orange focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">
                  Shift Hours
                </label>
                <input
                  type="number"
                  value={config.shiftHours}
                  onChange={(e) => handleConfigChange('shiftHours', e.target.value)}
                  className="w-full bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-swiggy-orange focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">
                  Max Orders per Rider/Day
                </label>
                <input
                  type="number"
                  value={config.maxOrdersPerDay}
                  onChange={(e) => handleConfigChange('maxOrdersPerDay', e.target.value)}
                  className="w-full bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-swiggy-orange focus:outline-none"
                />
              </div>
              <div className="pt-2 border-t border-slate-700">
                <p className="text-sm text-slate-400">
                  Daily Fixed Cost per Rider: <span className="text-white font-semibold">{formatINR(dailyFixedCost.toFixed(2))}</span>
                </p>
              </div>
            </div>
          </div>
          
          {/* Gig Fleet Section */}
          <div className="mb-6 bg-slate-800 p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-3 text-swiggy-orange flex items-center">
              <TrendingUp className="w-5 h-5 mr-2" />
              Gig Fleet (Variable Cost Model)
            </h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-slate-300 mb-1">
                  Base Payout per Order
                </label>
                <input
                  type="number"
                  value={config.basePayoutPerOrder}
                  onChange={(e) => handleConfigChange('basePayoutPerOrder', e.target.value)}
                  className="w-full bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-swiggy-orange focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">
                  Surge Multiplier
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={config.surgeMultiplier}
                  onChange={(e) => handleConfigChange('surgeMultiplier', e.target.value)}
                  className="w-full bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-swiggy-orange focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">
                  Gig Availability Cap
                </label>
                <input
                  type="number"
                  value={config.gigAvailabilityCap}
                  onChange={(e) => handleConfigChange('gigAvailabilityCap', e.target.value)}
                  className="w-full bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-swiggy-orange focus:outline-none"
                />
              </div>
            </div>
          </div>
          
          {/* Demand Scenario Section */}
          <div className="mb-6 bg-slate-800 p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-3 text-swiggy-orange">
              Demand Scenario (7-Day Week)
            </h2>
            <div className="space-y-2">
              {config.demandScenario.map((item, index) => (
                <div key={item.day} className="flex items-center justify-between">
                  <label className="text-sm text-slate-300 w-24">
                    {item.day}
                  </label>
                  <input
                    type="number"
                    value={item.orders}
                    onChange={(e) => handleDemandChange(index, e.target.value)}
                    className="flex-1 ml-3 bg-slate-700 text-white px-3 py-2 rounded border border-slate-600 focus:border-swiggy-orange focus:outline-none"
                  />
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* RIGHT PANEL - Simulation Dashboard */}
        <div className="w-1/2 overflow-y-auto p-6">
          <div className="mb-6">
            <h2 className="text-2xl font-bold mb-4">Simulation Dashboard</h2>
            
            {/* User Input Sliders */}
            <div className="bg-slate-800 p-4 rounded-lg mb-6">
              <div className="mb-4">
                <label className="block text-sm text-slate-300 mb-2">
                  Permanent Fleet Size: <span className="text-swiggy-orange font-semibold">{fleetSize}</span> riders
                </label>
                <input
                  type="range"
                  min="0"
                  max="1000"
                  value={fleetSize}
                  onChange={(e) => setFleetSize(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-swiggy-orange"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-2">
                  Target Utilization: <span className="text-swiggy-orange font-semibold">{targetUtilization}%</span>
                </label>
                <input
                  type="range"
                  min="50"
                  max="100"
                  value={targetUtilization}
                  onChange={(e) => setTargetUtilization(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-swiggy-orange"
                />
              </div>
            </div>
            
            {/* KPI Cards */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-slate-800 p-4 rounded-lg">
                <div className="flex items-center mb-2">
                  <Bike className="w-5 h-5 text-swiggy-orange mr-2" />
                  <h3 className="text-sm text-slate-400">Fleet Utilization Rate</h3>
                </div>
                <p className={`text-2xl font-bold ${weeklyMetrics.avgUtilization < 70 ? 'text-red-500' : 'text-green-500'}`}>
                  {weeklyMetrics.avgUtilization.toFixed(1)}%
                </p>
                {weeklyMetrics.avgUtilization < 70 && (
                  <p className="text-xs text-red-400 mt-1 flex items-center">
                    <AlertTriangle className="w-3 h-3 mr-1" />
                    Overstaffed
                  </p>
                )}
              </div>
              
              <div className="bg-slate-800 p-4 rounded-lg">
                <div className="flex items-center mb-2">
                  <DollarSign className="w-5 h-5 text-swiggy-orange mr-2" />
                  <h3 className="text-sm text-slate-400">Avg Cost Per Order</h3>
                </div>
                <p className="text-2xl font-bold">
                  {formatINR(weeklyMetrics.avgCostPerOrder.toFixed(2))}
                </p>
              </div>
            </div>
            
            {/* Breakeven Comparator */}
            <div className="bg-slate-800 p-4 rounded-lg mb-6">
              <h3 className="text-lg font-semibold mb-4">Breakeven Comparator</h3>
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Hybrid Model (Current)</p>
                  <p className="text-xl font-semibold">{formatINRLakhs(weeklyMetrics.hybridCost)}</p>
                </div>
                <div>
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
            
            {/* Utilization Trap Chart */}
            <div className="bg-slate-800 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">The "Utilization Trap" Chart</h3>
              <ResponsiveContainer width="100%" height={300}>
                <ComposedChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                  <XAxis 
                    dataKey="day" 
                    stroke="#94a3b8"
                    style={{ fontSize: '12px' }}
                  />
                  <YAxis 
                    stroke="#94a3b8"
                    style={{ fontSize: '12px' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1e293b', 
                      border: '1px solid #475569',
                      borderRadius: '8px'
                    }}
                    formatter={(value) => value.toLocaleString()}
                  />
                  <Legend />
                  
                  {/* Highlight overCapacity days */}
                  {chartData.map((entry, index) => {
                    if (entry.isOverCapacity) {
                      return (
                        <ReferenceArea
                          key={`over-${index}`}
                          x1={index > 0 ? chartData[index - 1].day : entry.day}
                          x2={index < chartData.length - 1 ? chartData[index + 1].day : entry.day}
                          fill="#ef4444"
                          fillOpacity={0.1}
                          label={{
                            value: 'CASH BURN',
                            position: 'top',
                            fill: '#ef4444',
                            fontSize: 10
                          }}
                        />
                      );
                    }
                    return null;
                  })}
                  
                  <Bar 
                    dataKey="permCapacity" 
                    stackId="a" 
                    fill="#FC8019" 
                    name="Permanent Capacity"
                  />
                  <Bar 
                    dataKey="gigOrders" 
                    stackId="a" 
                    fill="#64748b" 
                    name="Gig Orders"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="demand" 
                    stroke="#ffffff" 
                    strokeWidth={2}
                    name="Actual Demand"
                    dot={{ fill: '#ffffff', r: 4 }}
                  />
                </ComposedChart>
              </ResponsiveContainer>
              <p className="text-xs text-slate-400 mt-2">
                Orange bars show permanent capacity. Gray bars show gig overflow. White line shows actual demand. Red zones indicate idle capacity (CASH BURN).
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SwiggyFleetSimulator;

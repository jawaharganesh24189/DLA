import React, { useState, useMemo } from 'react';
import ConfigPanel from './components/ConfigPanel';
import Dashboard from './components/Dashboard';

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
      [field]: value
    }));
  };
  
  // Handle demand scenario changes
  const handleDemandChange = (index, value) => {
    setConfig(prev => ({
      ...prev,
      demandScenario: prev.demandScenario.map((item, i) => 
        i === index ? { ...item, orders: value } : item
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
        <ConfigPanel 
          config={config}
          onConfigChange={handleConfigChange}
          onDemandChange={handleDemandChange}
        />
        <Dashboard
          fleetSize={fleetSize}
          targetUtilization={targetUtilization}
          onFleetSizeChange={setFleetSize}
          onUtilizationChange={setTargetUtilization}
          weeklyMetrics={weeklyMetrics}
          chartData={chartData}
          simulationResults={simulationResults}
        />
      </div>
    </div>
  );
};

export default SwiggyFleetSimulator;

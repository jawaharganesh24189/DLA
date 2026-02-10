import React from 'react';
import { DollarSign, Bike, TrendingUp } from 'lucide-react';
import Slider from './Slider';

const ConfigPanel = ({ config, onConfigChange, onDemandChange }) => {
  return (
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
          <Slider
            label="Avg Order Value (AOV)"
            value={config.aov}
            min={100}
            max={1000}
            step={10}
            onChange={(value) => onConfigChange('aov', value)}
            unit="₹"
          />
          <Slider
            label="Commission Rate"
            value={config.commissionRate}
            min={10}
            max={40}
            step={1}
            onChange={(value) => onConfigChange('commissionRate', value)}
            unit="%"
          />
          <Slider
            label="Customer Delivery Fee"
            value={config.deliveryFee}
            min={0}
            max={100}
            step={5}
            onChange={(value) => onConfigChange('deliveryFee', value)}
            unit="₹"
          />
        </div>
      </div>
      
      {/* Permanent Fleet Section */}
      <div className="mb-6 bg-slate-800 p-4 rounded-lg">
        <h2 className="text-xl font-semibold mb-3 text-swiggy-orange flex items-center">
          <Bike className="w-5 h-5 mr-2" />
          Permanent Fleet (Fixed Cost Model)
        </h2>
        <div className="space-y-3">
          <Slider
            label="Monthly Salary (CTC)"
            value={config.monthlySalary}
            min={15000}
            max={40000}
            step={1000}
            onChange={(value) => onConfigChange('monthlySalary', value)}
            unit="₹"
          />
          <Slider
            label="Daily Fuel/Maintenance Allowance"
            value={config.dailyAllowance}
            min={50}
            max={500}
            step={10}
            onChange={(value) => onConfigChange('dailyAllowance', value)}
            unit="₹"
          />
          <Slider
            label="Insurance/Benefits per Rider (Monthly)"
            value={config.monthlyInsurance}
            min={500}
            max={5000}
            step={100}
            onChange={(value) => onConfigChange('monthlyInsurance', value)}
            unit="₹"
          />
          <Slider
            label="Shift Hours"
            value={config.shiftHours}
            min={6}
            max={14}
            step={1}
            onChange={(value) => onConfigChange('shiftHours', value)}
            unit=" hrs"
          />
          <Slider
            label="Max Orders per Rider/Day"
            value={config.maxOrdersPerDay}
            min={10}
            max={40}
            step={1}
            onChange={(value) => onConfigChange('maxOrdersPerDay', value)}
            unit=""
          />
          <div className="pt-2 border-t border-slate-700">
            <p className="text-sm text-slate-400">
              Daily Fixed Cost per Rider: <span className="text-white font-semibold">
                ₹{(((config.monthlySalary + config.monthlyInsurance) / 30) + config.dailyAllowance).toFixed(2)}
              </span>
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
          <Slider
            label="Base Payout per Order"
            value={config.basePayoutPerOrder}
            min={20}
            max={100}
            step={5}
            onChange={(value) => onConfigChange('basePayoutPerOrder', value)}
            unit="₹"
          />
          <Slider
            label="Surge Multiplier"
            value={config.surgeMultiplier}
            min={1.0}
            max={3.0}
            step={0.1}
            onChange={(value) => onConfigChange('surgeMultiplier', value)}
            unit="x"
          />
          <Slider
            label="Gig Availability Cap"
            value={config.gigAvailabilityCap}
            min={1000}
            max={10000}
            step={500}
            onChange={(value) => onConfigChange('gigAvailabilityCap', value)}
            unit=""
          />
        </div>
      </div>
      
      {/* Demand Scenario Section */}
      <div className="mb-6 bg-slate-800 p-4 rounded-lg">
        <h2 className="text-xl font-semibold mb-3 text-swiggy-orange">
          Demand Scenario (7-Day Week)
        </h2>
        <div className="space-y-3">
          {config.demandScenario.map((item, index) => (
            <Slider
              key={item.day}
              label={item.day}
              value={item.orders}
              min={1000}
              max={20000}
              step={500}
              onChange={(value) => onDemandChange(index, value)}
              unit=" orders"
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default ConfigPanel;

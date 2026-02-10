import React, { useRef } from 'react';
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
import { Download } from 'lucide-react';
import { exportChartAsPNG } from '../utils/exportData';

const UtilizationChart = ({ chartData }) => {
  const chartRef = useRef(null);

  const handleExportChart = () => {
    exportChartAsPNG(chartRef.current, 'utilization-trap-chart');
  };

  return (
    <div className="bg-slate-800 p-4 rounded-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">The "Utilization Trap" Chart</h3>
        <button
          onClick={handleExportChart}
          className="flex items-center gap-2 px-3 py-1 bg-swiggy-orange text-white rounded hover:bg-orange-600 transition-colors text-sm"
        >
          <Download className="w-4 h-4" />
          Export
        </button>
      </div>
      <div ref={chartRef}>
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
      </div>
      <p className="text-xs text-slate-400 mt-2">
        Orange bars show permanent capacity. Gray bars show gig overflow. White line shows actual demand. Red zones indicate idle capacity (CASH BURN).
      </p>
    </div>
  );
};

export default UtilizationChart;

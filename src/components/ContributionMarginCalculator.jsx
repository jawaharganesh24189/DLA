import React, { useState } from 'react';
import { GripVertical, Plus, Trash2 } from 'lucide-react';
import { formatINR, formatINRLakhs } from '../utils/formatters';

const ContributionMarginCalculator = ({ weeklyMetrics }) => {
  const [parameters, setParameters] = useState([
    { id: 1, name: 'Total Revenue', value: weeklyMetrics.totalRevenue, type: 'revenue' },
    { id: 2, name: 'Fixed Costs', value: weeklyMetrics.hybridCost * 0.6, type: 'cost' },
    { id: 3, name: 'Variable Costs', value: weeklyMetrics.hybridCost * 0.4, type: 'cost' },
  ]);

  const [draggedItem, setDraggedItem] = useState(null);
  const [newParamName, setNewParamName] = useState('');
  const [newParamValue, setNewParamValue] = useState('');
  const [newParamType, setNewParamType] = useState('cost');

  const handleDragStart = (e, index) => {
    setDraggedItem(index);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e, index) => {
    e.preventDefault();
    if (draggedItem === index) return;

    const newParameters = [...parameters];
    const draggedParameter = newParameters[draggedItem];
    newParameters.splice(draggedItem, 1);
    newParameters.splice(index, 0, draggedParameter);

    setDraggedItem(index);
    setParameters(newParameters);
  };

  const handleDragEnd = () => {
    setDraggedItem(null);
  };

  const handleAddParameter = () => {
    if (newParamName && newParamValue) {
      const newParam = {
        id: Date.now(),
        name: newParamName,
        value: parseFloat(newParamValue),
        type: newParamType
      };
      setParameters([...parameters, newParam]);
      setNewParamName('');
      setNewParamValue('');
    }
  };

  const handleDeleteParameter = (id) => {
    setParameters(parameters.filter(param => param.id !== id));
  };

  const handleValueChange = (id, newValue) => {
    setParameters(parameters.map(param => 
      param.id === id ? { ...param, value: parseFloat(newValue) || 0 } : param
    ));
  };

  const totalRevenue = parameters
    .filter(p => p.type === 'revenue')
    .reduce((sum, p) => sum + p.value, 0);
  
  const totalCosts = parameters
    .filter(p => p.type === 'cost')
    .reduce((sum, p) => sum + p.value, 0);

  const contributionMargin = totalRevenue - totalCosts;
  const contributionMarginPercent = totalRevenue > 0 ? (contributionMargin / totalRevenue) * 100 : 0;

  return (
    <div className="bg-slate-800 p-4 rounded-lg mb-6">
      <h3 className="text-lg font-semibold mb-4 text-swiggy-orange">Contribution Margin Calculator</h3>
      
      {/* Parameter List */}
      <div className="space-y-2 mb-4">
        {parameters.map((param, index) => (
          <div
            key={param.id}
            draggable
            onDragStart={(e) => handleDragStart(e, index)}
            onDragOver={(e) => handleDragOver(e, index)}
            onDragEnd={handleDragEnd}
            className={`flex items-center gap-2 p-3 rounded ${
              param.type === 'revenue' ? 'bg-green-900/20 border border-green-700' : 'bg-red-900/20 border border-red-700'
            } cursor-move hover:bg-slate-700 transition-colors`}
          >
            <GripVertical className="w-4 h-4 text-slate-500" />
            <div className="flex-1">
              <p className="text-sm font-medium">{param.name}</p>
              <input
                type="number"
                value={param.value}
                onChange={(e) => handleValueChange(param.id, e.target.value)}
                className="w-full mt-1 bg-slate-700 text-white px-2 py-1 rounded text-sm"
                onClick={(e) => e.stopPropagation()}
              />
            </div>
            <div className="text-right">
              <span className={`text-sm font-semibold ${param.type === 'revenue' ? 'text-green-400' : 'text-red-400'}`}>
                {param.type === 'revenue' ? '+' : '-'} {formatINRLakhs(param.value)}
              </span>
            </div>
            <button
              onClick={() => handleDeleteParameter(param.id)}
              className="p-1 hover:bg-red-600 rounded transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>

      {/* Add New Parameter */}
      <div className="p-3 bg-slate-700 rounded mb-4">
        <p className="text-sm text-slate-300 mb-2">Add New Parameter</p>
        <div className="grid grid-cols-3 gap-2">
          <input
            type="text"
            placeholder="Parameter name"
            value={newParamName}
            onChange={(e) => setNewParamName(e.target.value)}
            className="bg-slate-600 text-white px-2 py-1 rounded text-sm"
          />
          <input
            type="number"
            placeholder="Value"
            value={newParamValue}
            onChange={(e) => setNewParamValue(e.target.value)}
            className="bg-slate-600 text-white px-2 py-1 rounded text-sm"
          />
          <select
            value={newParamType}
            onChange={(e) => setNewParamType(e.target.value)}
            className="bg-slate-600 text-white px-2 py-1 rounded text-sm"
          >
            <option value="revenue">Revenue</option>
            <option value="cost">Cost</option>
          </select>
        </div>
        <button
          onClick={handleAddParameter}
          className="mt-2 w-full flex items-center justify-center gap-2 py-2 bg-swiggy-orange text-white rounded hover:bg-orange-600 transition-colors text-sm"
        >
          <Plus className="w-4 h-4" />
          Add Parameter
        </button>
      </div>

      {/* Summary */}
      <div className="border-t border-slate-600 pt-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-slate-400">Total Revenue:</span>
          <span className="text-green-400 font-semibold">{formatINRLakhs(totalRevenue)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-slate-400">Total Costs:</span>
          <span className="text-red-400 font-semibold">{formatINRLakhs(totalCosts)}</span>
        </div>
        <div className="flex justify-between text-lg font-bold pt-2 border-t border-slate-600">
          <span>Contribution Margin:</span>
          <div className="text-right">
            <span className={contributionMargin >= 0 ? 'text-green-400' : 'text-red-400'}>
              {formatINRLakhs(contributionMargin)}
            </span>
            <span className="text-sm text-slate-400 ml-2">
              ({contributionMarginPercent.toFixed(1)}%)
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContributionMarginCalculator;

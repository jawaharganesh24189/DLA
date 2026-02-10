import React from 'react';

const Slider = ({ label, value, min, max, step = 1, onChange, unit = '', icon: Icon, color = 'swiggy-orange' }) => {
  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-2">
        <label className="flex items-center text-sm text-slate-300">
          {Icon && <Icon className="w-4 h-4 mr-2" />}
          {label}
        </label>
        <span className={`text-${color} font-semibold text-sm`}>
          {unit && unit === '₹' ? `₹${value.toLocaleString('en-IN')}` : `${value}${unit}`}
        </span>
      </div>
      <div className="relative">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className={`w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-${color} hover:bg-slate-600 transition-colors`}
        />
        <div className="flex justify-between text-xs text-slate-500 mt-1">
          <span>{unit && unit === '₹' ? `₹${min.toLocaleString('en-IN')}` : `${min}${unit}`}</span>
          <span>{unit && unit === '₹' ? `₹${max.toLocaleString('en-IN')}` : `${max}${unit}`}</span>
        </div>
      </div>
    </div>
  );
};

export default Slider;

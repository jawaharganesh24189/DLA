// Export simulation data as CSV
export const exportToCSV = (simulationResults, weeklyMetrics) => {
  const headers = [
    'Day',
    'Projected Orders',
    'Permanent Capacity',
    'Gig Orders',
    'Fixed Cost',
    'Gig Cost',
    'Total Revenue',
    'Net Margin',
    'Utilization %'
  ];

  const rows = simulationResults.map(result => [
    result.day,
    result.projectedOrders,
    result.permCapacity,
    result.gigOrdersNeeded,
    result.fixedFleetCost.toFixed(2),
    result.gigFleetCost.toFixed(2),
    result.totalRevenue.toFixed(2),
    result.netMargin.toFixed(2),
    result.actualUtilization.toFixed(2)
  ]);

  // Add weekly summary
  rows.push([]);
  rows.push(['Weekly Summary']);
  rows.push(['Total Orders', weeklyMetrics.totalOrders]);
  rows.push(['Total Cost', weeklyMetrics.totalCost.toFixed(2)]);
  rows.push(['Total Revenue', weeklyMetrics.totalRevenue.toFixed(2)]);
  rows.push(['Net Margin', weeklyMetrics.totalNetMargin.toFixed(2)]);
  rows.push(['Avg Utilization %', weeklyMetrics.avgUtilization.toFixed(2)]);
  rows.push(['Avg Cost Per Order', weeklyMetrics.avgCostPerOrder.toFixed(2)]);

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `swiggy-fleet-simulation-${new Date().toISOString().split('T')[0]}.csv`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// Export chart as PNG image
export const exportChartAsPNG = (chartRef, filename = 'chart') => {
  if (!chartRef) return;

  // For Recharts, we need to get the SVG element
  const svgElement = chartRef.querySelector('svg');
  if (!svgElement) return;

  const svgData = new XMLSerializer().serializeToString(svgElement);
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const img = new Image();

  const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(svgBlob);

  img.onload = () => {
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.fillStyle = '#0f172a'; // slate-900 background
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);
    
    canvas.toBlob((blob) => {
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${filename}-${new Date().toISOString().split('T')[0]}.png`;
      link.click();
    });
    
    URL.revokeObjectURL(url);
  };

  img.src = url;
};

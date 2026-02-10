// Utility function to format Indian currency
export const formatINR = (amount) => {
  return `₹${amount.toLocaleString('en-IN')}`;
};

export const formatINRLakhs = (amount) => {
  const lakhs = amount / 100000;
  return `₹${lakhs.toFixed(2)} L`;
};

export const formatPercentage = (value) => {
  return `${value.toFixed(1)}%`;
};

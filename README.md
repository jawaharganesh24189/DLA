# Swiggy Fleet Strategy Simulator

A comprehensive web application built with **React**, **Tailwind CSS**, and **Recharts** that simulates the financial impact of shifting from a 100% Gig-worker model to a Permanent (Fixed Salary) Fleet model.

![Swiggy Fleet Strategy Simulator](https://github.com/user-attachments/assets/73e87a8f-4db7-435a-b551-468bd0d02beb)

## Features

### 1. Theme & UX
- **Swiggy Corporate Strategy** aesthetic with Swiggy Orange (#FC8019) as the primary accent
- Dark Mode with Slate-900 backgrounds and crisp white text
- Split View Layout: Admin/Config Panel (left) and Simulation Dashboard (right)
- Professional, data-dense "Command Center" feel

### 2. Admin Dashboard (Left Panel)
Comprehensive configuration form with editable parameters grouped by category:

#### A. Unit Economics (Revenue)
- Avg Order Value (AOV): Default ₹400
- Commission Rate %: Default 22%
- Customer Delivery Fee: Default ₹30

#### B. Permanent Fleet (Fixed Cost Model)
- Monthly Salary (CTC): Default ₹22,000
- Daily Fuel/Maintenance Allowance: Default ₹150
- Insurance/Benefits per Rider (Monthly): Default ₹2,000
- Shift Hours: Default 10
- Max Orders per Rider/Day: Default 22
- Calculated Daily Fixed Cost displayed

#### C. Gig Fleet (Variable Cost Model)
- Base Payout per Order: Default ₹45
- Surge Multiplier: Default 1.6x
- Gig Availability Cap: Default 5000

#### D. Demand Scenario (7-Day Week)
- Editable table for projected orders each day
- Defaults: Mon-Thu: 8,500 | Fri: 11,000 | Sat-Sun: 14,500

### 3. Simulation Dashboard (Right Panel)

#### Interactive Controls
- **Permanent Fleet Size Slider**: 0-1000 riders
- **Target Utilization Slider**: 50-100%

#### Visualizations
- **The "Utilization Trap" Chart**: ComposedChart showing permanent capacity (orange), gig orders (gray), and actual demand (white line) with "CASH BURN" zones highlighted
- **Breakeven Comparator**: Side-by-side comparison of Hybrid vs 100% Gig model with savings/loss calculations
- **KPI Cards**: 
  - Fleet Utilization Rate (warns if < 70%)
  - Avg Cost Per Order

### 4. Simulation Logic
Real-time calculations for each day including:
- Permanent capacity based on fleet size and utilization
- Gig orders spillover when demand exceeds capacity
- Idle waste detection and cost calculation
- Surge pricing when gig orders exceed 30% of demand
- Revenue and profitability metrics

## Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Technologies Used
- **React 18** - UI framework
- **Vite 8** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Lucide React** - Icons

## Project Structure
```
/src
  ├── App.jsx          # Main application component with all logic
  ├── index.css        # Tailwind CSS imports
  └── main.jsx         # Application entry point
```

## Development
The application features instant recalculation on any parameter change, providing real-time insights into fleet strategy decisions.


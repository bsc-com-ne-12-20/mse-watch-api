# Historical Data API - React Integration Guide

## **Quick Reference**

**Endpoint**: `GET /api/historical/{symbol}/`  
**Authentication**: Required - `X-API-Key` header  
**Response**: JSON with historical price data  

---

## **Request Parameters**

### Required
- **symbol** (path): Stock symbol (`AIRTEL`, `TNM`, `NBM`, etc.)
- **X-API-Key** (header): Your API key

### Optional Query Parameters
| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| `range` | `1month` | `1month`, `3months`, `6months`, `1year`, `2years`, `5years` | Time range |
| `cache` | `true` | `true`, `false` | Use cached data |
| `refresh` | `false` | `true`, `false` | Force fresh data |

---

## **Supported Symbols**
`AIRTEL`, `TNM`, `NBM`, `STANDARD`, `BHL`, `FDHB`, `FMBCH`, `ICON`, `ILLOVO`, `MPICO`, `NBS`, `NICO`, `NITL`, `OMU`, `PCL`, `SUNBIRD`

---

## **React Hooks & Components**

### Custom Hook - useHistoricalData
```jsx
import { useState, useEffect } from 'react';

const useHistoricalData = (symbol, range = '3months', apiKey) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async (forceRefresh = false) => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({ range });
      if (forceRefresh) params.append('refresh', 'true');

      const response = await fetch(`/api/historical/${symbol}/?${params}`, {
        headers: { 'X-API-Key': apiKey }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      setData(result);

      // Handle data limitations
      if (result.data_limitation) {
        console.warn('Data limitation:', result.data_limitation);
      }

    } catch (err) {
      setError(err.message);
      console.error('Historical data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (symbol && apiKey) {
      fetchData();
    }
  }, [symbol, range, apiKey]);

  return { data, loading, error, refetch: () => fetchData(true) };
};

export default useHistoricalData;
```

### React Component Example
```jsx
import React, { useState } from 'react';
import useHistoricalData from './hooks/useHistoricalData';

const StockChart = ({ apiKey }) => {
  const [symbol, setSymbol] = useState('AIRTEL');
  const [range, setRange] = useState('3months');
  
  const { data, loading, error, refetch } = useHistoricalData(symbol, range, apiKey);

  if (loading) return <div>Loading chart data...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>No data available</div>;

  return (
    <div className="stock-chart">
      <div className="controls">
        <select value={symbol} onChange={(e) => setSymbol(e.target.value)}>
          <option value="AIRTEL">AIRTEL</option>
          <option value="TNM">TNM</option>
          <option value="NBM">NBM</option>
          {/* Add more symbols */}
        </select>
        
        <select value={range} onChange={(e) => setRange(e.target.value)}>
          <option value="1month">1 Month</option>
          <option value="3months">3 Months</option>
          <option value="6months">6 Months</option>
          <option value="1year">1 Year</option>
        </select>
        
        <button onClick={refetch}>Refresh</button>
      </div>

      {data.data_limitation && (
        <div className="warning">
          ⚠️ {data.data_limitation}
        </div>
      )}

      <div className="chart-info">
        <h3>{data.company.name} ({data.company.symbol})</h3>
        <p>Current Price: ${data.company.current_price}</p>
        <p>Data Points: {data.data_points}</p>
      </div>

      {/* Your chart component here */}
      <ChartComponent data={data.stock_prices} />
    </div>
  );
};
```

---

## **Response Structure**

### Success Response (200)
```json
{
  "company": {
    "symbol": "AIRTEL",
    "name": "Airtel Malawi PLC",
    "current_price": 127.98
  },
  "time_range": "3months",
  "data_points": 60,
  "source": "cache",
  "retrieved_at": "2025-06-21T14:30:00.000000",
  "stock_prices": [
    {
      "date": "2025-03-21",
      "price": 127.98,
      "close": 127.98,
      "open": null,
      "high": null,
      "low": null,
      "volume": null,
      "turnover": null
    }
    // ... more data points
  ]
}
```

### Limited Data Response
```json
{
  // ... same as above, plus:
  "data_limitation": "Limited data available: 119 points (expected ~240)",
  "note": "Database contains limited historical data for this time range"
}
```

---

## **Key Response Fields for Frontend**

| Field | Type | Use Case |
|-------|------|----------|
| `company.symbol` | string | Display stock symbol |
| `company.name` | string | Display company name |
| `company.current_price` | number | Show latest price |
| `data_points` | number | Data availability indicator |
| `time_range` | string | Confirm requested range |
| `source` | string | Performance indicator (`cache` = fast) |
| `data_limitation` | string | Show warning if present |
| `stock_prices[]` | array | Chart data points |
| `stock_prices[].date` | string | X-axis (YYYY-MM-DD format) |
| `stock_prices[].price` | number | Y-axis (main price value) |

---

## **Error Handling**

### Error Responses
```json
// Invalid symbol (404)
{
  "error": "Could not retrieve historical data for XYZ",
  "message": "Data may not be available for this symbol"
}

// Auth error (401)
{
  "error": "API key required",
  "message": "Please provide a valid API key"
}

// Rate limit (429)
{
  "error": "Quota exceeded",
  "message": "Monthly API call limit reached"
}
```

## **React Error Handling Components**

### Error Boundary
```jsx
import React from 'react';

class ApiErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('API Error Boundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h3>Something went wrong with the API</h3>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false, error: null })}>
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Error Display Component
```jsx
const ErrorDisplay = ({ error, onRetry }) => {
  const getErrorMessage = (error) => {
    if (error.includes('401')) return 'Invalid API key. Please check your credentials.';
    if (error.includes('429')) return 'Rate limit exceeded. Please try again later.';
    if (error.includes('404')) return 'Stock symbol not found.';
    return 'An unexpected error occurred. Please try again.';
  };

  return (
    <div className="error-display">
      <h4>⚠️ Error Loading Data</h4>
      <p>{getErrorMessage(error)}</p>
      {onRetry && (
        <button onClick={onRetry} className="retry-button">
          Retry
        </button>
      )}
    </div>
  );
};
```

### Loading Component
```jsx
const LoadingSpinner = ({ message = "Loading..." }) => (
  <div className="loading-spinner">
    <div className="spinner"></div>
    <p>{message}</p>
  </div>
);

// CSS for spinner
// .spinner {
//   border: 4px solid #f3f3f3;
//   border-top: 4px solid #3498db;
//   border-radius: 50%;
//   width: 40px;
//   height: 40px;
//   animation: spin 2s linear infinite;
// }
// @keyframes spin {
//   0% { transform: rotate(0deg); }
//   100% { transform: rotate(360deg); }
// }
```

---

## **Performance Tips**

### Response Times
- **Cached data**: ~30-50ms ⚡
- **Fresh data**: ~2-3 seconds 🔄

### Best Practices
1. **Use cache by default** - Only set `refresh=true` when needed
2. **Show loading states** - Fresh data takes 2-3 seconds
3. **Handle data limitations** - Check for `data_limitation` field
4. **Implement retry logic** - For network failures
5. **Cache locally** - Store responses to reduce API calls

### Chart Integration with Chart.js
```jsx
import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const ChartComponent = ({ data }) => {
  const chartData = {
    labels: data.map(item => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Stock Price',
        data: data.map(item => item.price),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Historical Stock Prices',
      },
    },
    scales: {
      y: {
        beginAtZero: false,
      },
    },
  };

  return <Line data={chartData} options={options} />;
};
```

### Context Provider for API
```jsx
import React, { createContext, useContext } from 'react';

const ApiContext = createContext();

export const ApiProvider = ({ children, apiKey, baseUrl = '/api' }) => {
  const value = { apiKey, baseUrl };
  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
};

export const useApi = () => {
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
};

// Usage in your app
// <ApiProvider apiKey="your_api_key">
//   <App />
// </ApiProvider>
```

### Enhanced Hook with Context
```jsx
import { useState, useEffect } from 'react';
import { useApi } from './ApiContext';

const useHistoricalData = (symbol, range = '3months') => {
  const { apiKey, baseUrl } = useApi();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async (forceRefresh = false) => {
    if (!symbol || !apiKey) return;
    
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({ range });
      if (forceRefresh) params.append('refresh', 'true');

      const response = await fetch(`${baseUrl}/historical/${symbol}/?${params}`, {
        headers: { 'X-API-Key': apiKey }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      const result = await response.json();
      setData(result);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [symbol, range, apiKey]);

  return { 
    data, 
    loading, 
    error, 
    refetch: () => fetchData(true),
    isLimited: data?.data_limitation ? true : false 
  };
};
```

---

## **Data Availability Status**

| Range | Status | Data Points |
|-------|--------|-------------|
| `1month` | ✅ Full | ~22 |
| `3months` | ✅ Full | ~60 |
| `6months` | ✅ Full | ~120 |
| `1year` | ⚠️ Limited | ~248 (growing) |
| `2years` | ⚠️ Limited | ~248 |
| `5years` | ⚠️ Limited | ~248 |

**Note**: Longer ranges currently return limited data. Check `data_limitation` field in response.

---

## **Complete React Example**

```jsx
// App.js
import React from 'react';
import { ApiProvider } from './contexts/ApiContext';
import StockDashboard from './components/StockDashboard';
import './App.css';

function App() {
  return (
    <ApiProvider apiKey="your_api_key_here">
      <div className="App">
        <header className="App-header">
          <h1>MSE Stock Dashboard</h1>
        </header>
        <main>
          <StockDashboard />
        </main>
      </div>
    </ApiProvider>
  );
}

export default App;
```

```jsx
// components/StockDashboard.js
import React, { useState } from 'react';
import useHistoricalData from '../hooks/useHistoricalData';
import ChartComponent from './ChartComponent';
import ErrorDisplay from './ErrorDisplay';
import LoadingSpinner from './LoadingSpinner';
import ApiErrorBoundary from './ApiErrorBoundary';

const SYMBOLS = ['AIRTEL', 'TNM', 'NBM', 'STANDARD', 'BHL', 'FDHB'];
const RANGES = [
  { value: '1month', label: '1 Month' },
  { value: '3months', label: '3 Months' },
  { value: '6months', label: '6 Months' },
  { value: '1year', label: '1 Year' },
];

const StockDashboard = () => {
  const [symbol, setSymbol] = useState('AIRTEL');
  const [range, setRange] = useState('3months');
  
  const { data, loading, error, refetch, isLimited } = useHistoricalData(symbol, range);

  return (
    <ApiErrorBoundary>
      <div className="stock-dashboard">
        <div className="controls">
          <div className="control-group">
            <label htmlFor="symbol-select">Stock Symbol:</label>
            <select 
              id="symbol-select"
              value={symbol} 
              onChange={(e) => setSymbol(e.target.value)}
            >
              {SYMBOLS.map(sym => (
                <option key={sym} value={sym}>{sym}</option>
              ))}
            </select>
          </div>
          
          <div className="control-group">
            <label htmlFor="range-select">Time Range:</label>
            <select 
              id="range-select"
              value={range} 
              onChange={(e) => setRange(e.target.value)}
            >
              {RANGES.map(r => (
                <option key={r.value} value={r.value}>{r.label}</option>
              ))}
            </select>
          </div>
          
          <button onClick={refetch} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh Data'}
          </button>
        </div>

        {loading && <LoadingSpinner message="Fetching stock data..." />}
        
        {error && <ErrorDisplay error={error} onRetry={refetch} />}
        
        {data && !loading && (
          <div className="chart-container">
            {isLimited && (
              <div className="data-warning">
                ⚠️ {data.data_limitation}
              </div>
            )}
            
            <div className="stock-info">
              <h2>{data.company.name} ({data.company.symbol})</h2>
              <div className="info-grid">
                <div>Current Price: ${data.company.current_price}</div>
                <div>Data Points: {data.data_points}</div>
                <div>Source: {data.source}</div>
                <div>Updated: {new Date(data.retrieved_at).toLocaleString()}</div>
              </div>
            </div>
            
            <ChartComponent 
              data={data.stock_prices} 
              companyName={data.company.name}
            />
          </div>
        )}
      </div>
    </ApiErrorBoundary>
  );
};

export default StockDashboard;
```

## **TypeScript Support**

```typescript
// types/api.ts
export interface StockPrice {
  date: string;
  price: number;
  close: number;
  open: number | null;
  high: number | null;
  low: number | null;
  volume: number | null;
  turnover: number | null;
}

export interface Company {
  symbol: string;
  name: string;
  current_price: number;
  listing_date?: string;
  listing_price?: number;
  market_cap?: number | null;
  shares_in_issue?: number;
}

export interface HistoricalDataResponse {
  company: Company;
  time_range: string;
  data_points: number;
  source: 'cache' | 'mse.co.mw';
  retrieved_at: string;
  data_limitation?: string;
  note?: string;
  stock_prices: StockPrice[];
}

export type TimeRange = '1month' | '3months' | '6months' | '1year' | '2years' | '5years';
export type Symbol = 'AIRTEL' | 'TNM' | 'NBM' | 'STANDARD' | 'BHL' | 'FDHB' | 'FMBCH' | 'ICON' | 'ILLOVO' | 'MPICO' | 'NBS' | 'NICO' | 'NITL' | 'OMU' | 'PCL' | 'SUNBIRD';
```

```typescript
// hooks/useHistoricalData.ts
import { useState, useEffect } from 'react';
import { HistoricalDataResponse, TimeRange, Symbol } from '../types/api';
import { useApi } from '../contexts/ApiContext';

interface UseHistoricalDataReturn {
  data: HistoricalDataResponse | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
  isLimited: boolean;
}

const useHistoricalData = (
  symbol: Symbol, 
  range: TimeRange = '3months'
): UseHistoricalDataReturn => {
  const { apiKey, baseUrl } = useApi();
  const [data, setData] = useState<HistoricalDataResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async (forceRefresh = false): Promise<void> => {
    if (!symbol || !apiKey) return;
    
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({ range });
      if (forceRefresh) params.append('refresh', 'true');

      const response = await fetch(`${baseUrl}/historical/${symbol}/?${params}`, {
        headers: { 'X-API-Key': apiKey }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      const result: HistoricalDataResponse = await response.json();
      setData(result);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [symbol, range, apiKey]);

  return { 
    data, 
    loading, 
    error, 
    refetch: () => fetchData(true),
    isLimited: Boolean(data?.data_limitation)
  };
};

export default useHistoricalData;
```

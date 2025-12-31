# VALOR Dashboard - Setup Guide

## Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
cd valor-dashboard
npm install
```

### Step 2: Start Development Server
```bash
npm start
```

The dashboard will automatically open at `http://localhost:3000`

### Step 3: Login
- **Username**: `admin`
- **Password**: `valor2024`

That's it! You're now running the VALOR dashboard locally.

---

## Detailed Setup Instructions

### System Requirements
- **Node.js**: v16.0.0 or higher
- **npm**: v7.0.0 or higher (comes with Node.js)
- **RAM**: Minimum 4GB
- **Disk Space**: ~500MB for dependencies

### Installation Steps

#### 1. Verify Node.js Installation
```bash
node --version
npm --version
```

If not installed, download from [nodejs.org](https://nodejs.org/)

#### 2. Navigate to Project Directory
```bash
cd /path/to/valor-dashboard
```

#### 3. Install All Dependencies
```bash
npm install
```

This will install:
- React and React DOM
- React Router for navigation
- Chart.js for visualizations
- Axios for API calls
- Lucide React for icons
- Bootstrap and Reactstrap for UI
- And more...

#### 4. Start the Development Server
```bash
npm start
```

**What happens:**
- Webpack compiles the React app
- Development server starts on port 3000
- Browser automatically opens to `http://localhost:3000`
- Hot reload is enabled (changes auto-refresh)

---

## Configuration

### API Endpoints

The dashboard connects to your deployed Cloud Functions. These are configured in `src/services/api.js`:

```javascript
const API_BASE_URLS = {
  ingestEvents: 'https://ingest-events-ev2z3eeafa-ue.a.run.app',
  generateReport: 'https://generate-va-report-ev2z3eeafa-ue.a.run.app',
  getMetrics: 'https://get-confluent-metrics-ev2z3eeafa-ue.a.run.app',
  getSoldierSummary: 'https://get-soldier-summary-ev2z3eeafa-ue.a.run.app',
  getHealthAlerts: 'https://get-health-alerts-ev2z3eeafa-ue.a.run.app',
  resolveAlert: 'https://resolve-alert-ev2z3eeafa-ue.a.run.app'
};
```

**To update URLs:**
1. Open `src/services/api.js`
2. Modify the URLs as needed
3. Save the file (app will auto-reload)

### Polling Intervals

Different pages poll at different frequencies:

**Dashboard & Health Alerts** (10 seconds):
```javascript
// In src/pages/Dashboard.js and HealthAlerts.js
const interval = setInterval(fetchData, 10000); // 10 seconds
```

**Confluent Metrics** (30 seconds):
```javascript
// In src/pages/ConfluentMetrics.js
const interval = setInterval(fetchMetrics, 30000); // 30 seconds
```

**To adjust:**
- Change the millisecond value (10000 = 10 seconds)
- Shorter = more frequent updates, more API calls
- Longer = less frequent updates, fewer API calls

### Environment Variables (Optional)

Create a `.env` file in the project root:

```env
REACT_APP_API_BASE_URL=https://your-api-base-url.com
REACT_APP_POLLING_INTERVAL=10000
```

Then update `src/services/api.js`:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'default-url';
```

---

## Features Walkthrough

### 1. Login Page (`/login`)
- Simple authentication with demo credentials
- Uses localStorage to persist login state
- Redirects to dashboard on success

**Customize authentication:**
Edit `src/pages/Login.js` line 11-18 to integrate your auth system

### 2. Dashboard (`/dashboard`)
- **Real-time stats**: Total soldiers, alerts, health scores
- **Charts**: Alert trends and distribution
- **Live alerts table**: Recent critical alerts
- **Confluent status**: Data pipeline health

**Polls every 10 seconds for fresh data**

### 3. Health Alerts (`/alerts`)
- View all health alerts in real-time
- Filter by: All, Active, Critical
- Search by soldier ID or alert type
- Resolve alerts with one click

**Features:**
- Alert severity badges (Critical, High, Medium)
- Detailed alert information
- Location and timestamp tracking
- One-click resolution

### 4. VA Reports (`/reports`)
- Generate VA disability claim reports
- Enter soldier ID
- AI-powered analysis using Gemini
- Download generated reports

**How it works:**
1. Enter soldier ID (e.g., SGT_JOHNSON_001)
2. Click "Generate VA Report"
3. Wait 30-90 seconds for AI analysis
4. Download report PDF

### 5. Confluent Metrics (`/metrics`)
- Monitor Kafka cluster health
- Track topics and partitions
- View consumer groups
- Visualize throughput

**Key metrics:**
- Cluster status
- Topic count
- Consumer lag
- Messages per second

### 6. Devices (`/devices`)
- Track biometric sensors
- Monitor environmental stations
- View battery levels
- Check device status

**Device types:**
- Wearable biometric sensors
- Environmental monitors
- Burn pit detectors
- Heat stress monitors

### 7. Soldiers (`/soldiers`)
- Directory of all soldiers
- Search and filter
- View health scores
- Click for detailed profile

### 8. Soldier Profile (`/soldier/:id`)
- Complete soldier information
- Current vital signs
- Health score trend chart
- Recent health alerts
- Generate VA report

---

## Customization Guide

### Change Colors

Edit `src/styles/App.css`:

```css
:root {
  /* Background Colors */
  --primary-bg: #0a0e27;        /* Main dark background */
  --secondary-bg: #1a1f3a;      /* Cards and sidebar */
  --card-bg: #141728;           /* Card backgrounds */
  
  /* Accent Colors */
  --accent-green: #00ff88;      /* Success, healthy */
  --accent-amber: #ffa726;      /* Warning */
  --accent-red: #ff3860;        /* Critical, danger */
  --accent-blue: #00d4ff;       /* Info */
  
  /* Text Colors */
  --text-primary: #e8eaf0;      /* Main text */
  --text-secondary: #8898aa;    /* Secondary text */
  
  /* Border */
  --border-color: #2c3154;      /* Borders and dividers */
}
```

### Change Fonts

The dashboard uses **Rajdhani** for headers and **Poppins** for body text.

**To change:**
1. Update `public/index.html` Google Fonts link
2. Update `src/styles/App.css` font-family declarations

### Add New Pages

**Example: Add a "Settings" page**

1. **Create the page component**:
```javascript
// src/pages/Settings.js
import React from 'react';
import Navbar from '../components/Navbar';

const Settings = () => {
  return (
    <div className="main-content">
      <Navbar title="Settings" />
      <div className="card">
        <h2>Settings Page</h2>
      </div>
    </div>
  );
};

export default Settings;
```

2. **Add route in App.js**:
```javascript
import Settings from './pages/Settings';

// Inside <Routes>
<Route
  path="/settings"
  element={
    <ProtectedRoute>
      <Layout>
        <Settings />
      </Layout>
    </ProtectedRoute>
  }
/>
```

3. **Add to sidebar navigation**:
```javascript
// In src/components/Sidebar.js
import { Settings as SettingsIcon } from 'lucide-react';

// Add to navItems array
{ path: '/settings', icon: SettingsIcon, label: 'Settings' }
```

---

## Production Deployment

### Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` folder.

**Output:**
- Minified JavaScript bundles
- Optimized CSS
- Compressed images
- Service worker for caching

### Deploy to Firebase Hosting

1. **Install Firebase CLI**:
```bash
npm install -g firebase-tools
```

2. **Login to Firebase**:
```bash
firebase login
```

3. **Initialize Firebase**:
```bash
firebase init hosting
```

Configuration:
- Public directory: `build`
- Single-page app: `Yes`
- GitHub auto-deploy: `No`

4. **Deploy**:
```bash
npm run build
firebase deploy
```

### Deploy to Netlify

1. **Install Netlify CLI**:
```bash
npm install -g netlify-cli
```

2. **Login**:
```bash
netlify login
```

3. **Deploy**:
```bash
npm run build
netlify deploy --prod --dir=build
```

### Deploy to Google Cloud Storage

1. **Build the app**:
```bash
npm run build
```

2. **Create a bucket**:
```bash
gsutil mb gs://valor-dashboard
```

3. **Upload files**:
```bash
gsutil -m cp -r build/* gs://valor-dashboard
```

4. **Make public**:
```bash
gsutil iam ch allUsers:objectViewer gs://valor-dashboard
```

5. **Enable website configuration**:
```bash
gsutil web set -m index.html -e index.html gs://valor-dashboard
```

---

## Troubleshooting

### Common Issues

#### 1. "npm install" fails

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

#### 2. Port 3000 already in use

**Solution:**
```bash
# Kill process on port 3000 (Mac/Linux)
lsof -ti:3000 | xargs kill -9

# Or use a different port
PORT=3001 npm start
```

#### 3. "Module not found" errors

**Solution:**
```bash
# Reinstall dependencies
rm -rf node_modules
npm install
```

#### 4. CORS errors when calling APIs

**Cause:** Cloud Functions need CORS headers

**Solution:**
Add to your Cloud Functions:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
```

#### 5. Charts not displaying

**Cause:** Chart.js not registered

**Solution:** Already handled in components with:
```javascript
import { Chart as ChartJS, /* ... */ } from 'chart.js';
ChartJS.register(/* ... */);
```

#### 6. Authentication loop

**Solution:**
```bash
# Clear browser localStorage
# In browser console:
localStorage.clear()
```

---

## Development Tips

### Hot Reload
The app automatically reloads when you save files. No need to refresh!

### Browser DevTools
- Press `F12` to open DevTools
- Use React DevTools extension for debugging
- Check Network tab for API calls

### Code Structure Best Practices
- Components: Reusable UI elements
- Pages: Full page views
- Services: API communication logic
- Styles: Global CSS in App.css

### Adding New API Endpoints

1. **Add to `src/services/api.js`**:
```javascript
getNewData: async () => {
  const response = await apiClient.get('https://new-endpoint.com');
  return response.data;
}
```

2. **Use in component**:
```javascript
import apiService from '../services/api';

const data = await apiService.getNewData();
```

---

## Performance Optimization

### Reduce Polling Frequency
If the app feels slow, increase polling intervals:
```javascript
// Change from 10 seconds to 30 seconds
setInterval(fetchData, 30000);
```

### Lazy Loading
For large apps, lazy load pages:
```javascript
const Dashboard = React.lazy(() => import('./pages/Dashboard'));

<Suspense fallback={<div>Loading...</div>}>
  <Dashboard />
</Suspense>
```

### Memoization
Prevent unnecessary re-renders:
```javascript
import { useMemo } from 'react';

const expensiveValue = useMemo(() => {
  return calculateExpensiveValue(data);
}, [data]);
```

---

## Security Considerations

### Authentication
Current implementation uses basic localStorage. For production:

1. **Use JWT tokens**
2. **Implement refresh tokens**
3. **Add session timeout**
4. **Use HTTPS only**

### API Security
- Add API keys to requests
- Implement rate limiting
- Use CORS properly
- Validate all inputs

### Data Protection
- Don't store sensitive data in localStorage
- Use encrypted connections
- Implement proper access controls

---

## Next Steps

1. **Test all features** - Click through every page
2. **Customize colors** - Match your brand
3. **Connect real APIs** - Replace mock data
4. **Add authentication** - Implement your auth system
5. **Deploy to production** - Choose a hosting platform

---

## Support & Resources

- **React Documentation**: https://react.dev
- **Chart.js Docs**: https://www.chartjs.org
- **React Router**: https://reactrouter.com
- **Lucide Icons**: https://lucide.dev

---

## Version History

- **v1.0.0** (2025-12-30)
  - Initial release
  - Full dashboard with 8 pages
  - Real-time data polling
  - Cloud Functions integration
  - Military dark theme

---

**Built with ❤️ for VALOR Health Monitoring System**
# VALOR Dashboard

A production-ready React dashboard for the VALOR Health Monitoring System. This dashboard provides real-time monitoring of soldier health metrics, alerts, VA report generation, Confluent data pipeline metrics, and device management.

## Features

- 🔐 **Authentication** - Secure login system
- 📊 **Real-time Dashboard** - Live health metrics and alerts with 10-second polling
- 🚨 **Health Alerts** - Monitor and resolve critical health alerts
- 📄 **VA Report Generation** - AI-powered VA disability claim reports
- 📈 **Confluent Metrics** - Monitor Kafka topics, consumer groups, and throughput
- 📡 **Device Management** - Track biometric sensors and environmental monitors
- 👥 **Soldier Profiles** - Detailed health tracking per soldier
- 🎨 **Military Dark Theme** - Professional dark UI with military aesthetics

## Tech Stack

- **React 18** - Frontend framework
- **React Router 6** - Navigation and routing
- **Chart.js & React-Chartjs-2** - Data visualization
- **Axios** - API communication
- **Lucide React** - Icon library
- **Reactstrap & Bootstrap 5** - UI components

## Installation

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Setup

1. **Clone or extract the project**
   ```bash
   cd valor-dashboard
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

   The app will open at `http://localhost:3000`

## Login Credentials

**Demo Account:**
- Username: `admin`
- Password: `valor2024`

## API Integration

The dashboard connects to your deployed Google Cloud Functions:

- **Ingest Events**: `https://ingest-events-ev2z3eeafa-ue.a.run.app`
- **Generate VA Report**: `https://generate-va-report-ev2z3eeafa-ue.a.run.app`
- **Get Confluent Metrics**: `https://get-confluent-metrics-ev2z3eeafa-ue.a.run.app`
- **Get Soldier Summary**: `https://get-soldier-summary-ev2z3eeafa-ue.a.run.app`
- **Get Health Alerts**: `https://get-health-alerts-ev2z3eeafa-ue.a.run.app`
- **Resolve Alert**: `https://resolve-alert-ev2z3eeafa-ue.a.run.app`

These URLs are configured in `src/services/api.js`.

## Real-time Updates

- **Health Alerts**: Polls every 10 seconds
- **Dashboard Stats**: Polls every 10 seconds
- **Confluent Metrics**: Polls every 30 seconds

## Project Structure

```
valor-dashboard/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/
│   │   ├── Navbar.js       # Top navigation bar
│   │   └── Sidebar.js      # Side navigation menu
│   ├── pages/
│   │   ├── Dashboard.js           # Main dashboard
│   │   ├── HealthAlerts.js        # Health alerts page
│   │   ├── VAReports.js           # VA report generation
│   │   ├── ConfluentMetrics.js    # Confluent monitoring
│   │   ├── Devices.js             # Device management
│   │   ├── Soldiers.js            # Soldiers list
│   │   ├── SoldierProfile.js      # Individual soldier view
│   │   └── Login.js               # Login page
│   ├── services/
│   │   └── api.js          # API service layer
│   ├── styles/
│   │   └── App.css         # Global styles
│   ├── App.js              # Main app with routing
│   └── index.js            # Entry point
├── package.json            # Dependencies
└── README.md              # This file
```

## Available Scripts

### `npm start`
Runs the app in development mode at [http://localhost:3000](http://localhost:3000)

### `npm run build`
Builds the app for production to the `build` folder. The build is optimized and minified.

### `npm test`
Runs the test suite (if tests are added)

## Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Hosting
The production build can be deployed to:
- **Google Cloud Storage** (Static Website)
- **Firebase Hosting**
- **Netlify**
- **Vercel**
- **AWS S3 + CloudFront**

Example deployment to Firebase:
```bash
npm install -g firebase-tools
firebase login
firebase init hosting
firebase deploy
```

## Pages Overview

### 1. Dashboard (`/dashboard`)
- Overview statistics
- Alert trends chart
- Alert distribution chart
- Recent critical alerts
- Confluent pipeline status

### 2. Health Alerts (`/alerts`)
- Real-time health alert monitoring
- Filter by status and severity
- Search functionality
- Alert resolution
- Detailed alert information

### 3. VA Reports (`/reports`)
- Generate VA disability claim reports
- View recent reports
- Download reports
- Report generation status

### 4. Confluent Metrics (`/metrics`)
- Cluster health status
- Topic monitoring
- Consumer group tracking
- Throughput visualization
- System information

### 5. Devices (`/devices`)
- Device status monitoring
- Battery level tracking
- Soldier assignments
- Live metrics display
- Filter by status

### 6. Soldiers (`/soldiers`)
- Soldier directory
- Search and filter
- Health score overview
- Individual profiles

### 7. Soldier Profile (`/soldier/:id`)
- Detailed soldier information
- Current vitals
- Health score trend
- Recent alerts
- Generate VA report

## Customization

### Colors
Edit `src/styles/App.css` CSS variables:
```css
:root {
  --primary-bg: #0a0e27;
  --accent-green: #00ff88;
  --accent-amber: #ffa726;
  --accent-red: #ff3860;
  /* ... */
}
```

### API Endpoints
Edit `src/services/api.js` to update Cloud Function URLs.

### Polling Intervals
Update polling intervals in component `useEffect` hooks:
```javascript
const interval = setInterval(fetchData, 10000); // 10 seconds
```

## Troubleshooting

### CORS Issues
If you encounter CORS errors, ensure your Cloud Functions have proper CORS headers configured.

### API Connection Errors
- Verify Cloud Function URLs are correct
- Check that functions are deployed and accessible
- Ensure proper authentication if required

### Build Errors
```bash
rm -rf node_modules package-lock.json
npm install
npm start
```

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## License

Proprietary - VALOR Health Monitoring System

## Support

For issues or questions, contact your system administrator.

---

**VALOR** - Protecting those who protect us 🇺🇸
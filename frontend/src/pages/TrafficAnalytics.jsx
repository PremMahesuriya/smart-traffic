import { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import apiService from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const PIE_COLORS = ['#22c55e', '#eab308', '#f97316', '#ef4444']; // Low, Medium, High, Very High

export default function TrafficAnalytics() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analyticsData, setAnalyticsData] = useState({
    avgCountData: [],
    densityData: [],
    historyData: [],
    signalUsageData: [],
  });

  const fetchData = async () => {
    try {
      setError(null);
      const [trafficHistory, signalHistory] = await Promise.all([
        apiService.getTrafficHistory(),
        apiService.getSignalHistory(),
      ]);

      // 1. Process Average Count per Lane
      const laneCounts = { A: { sum: 0, count: 0 }, B: { sum: 0, count: 0 }, C: { sum: 0, count: 0 }, D: { sum: 0, count: 0 } };
      trafficHistory.forEach(log => {
        if (laneCounts[log.lane]) {
          laneCounts[log.lane].sum += log.vehicleCount;
          laneCounts[log.lane].count += 1;
        }
      });
      const avgCountData = ['A', 'B', 'C', 'D'].map(lane => ({
        name: `Lane ${lane}`,
        avg: laneCounts[lane].count > 0 ? Math.round((laneCounts[lane].sum / laneCounts[lane].count) * 10) / 10 : 0
      }));

      // 2. Process Density Distribution
      const densities = { Low: 0, Medium: 0, High: 0, 'Very High': 0 };
      trafficHistory.forEach(log => {
        if (log.density in densities) {
          densities[log.density] += 1;
        }
      });
      const densityData = Object.keys(densities).map(key => ({
        name: key,
        value: densities[key]
      })).filter(d => d.value > 0);

      // 3. Process Historical Traffic Count over Time
      const timeGrouped = {};
      trafficHistory.forEach(log => {
        const timeKey = log.timestamp.toFixed(1);
        if (!timeGrouped[timeKey]) {
          timeGrouped[timeKey] = { time: `${timeKey}s`, A: 0, B: 0, C: 0, D: 0 };
        }
        timeGrouped[timeKey][log.lane] = log.vehicleCount;
      });
      const historyData = Object.values(timeGrouped)
        .sort((a, b) => parseFloat(a.time) - parseFloat(b.time))
        .slice(-25); // Get last 25 time steps

      // 4. Process Signal Usage (Green allocations per lane)
      const signalUsage = { A: 0, B: 0, C: 0, D: 0 };
      signalHistory.forEach(log => {
        if (log.signalState === 'GREEN' && log.activeLane in signalUsage) {
          signalUsage[log.activeLane] += 1;
        }
      });
      const signalUsageData = ['A', 'B', 'C', 'D'].map(lane => ({
        name: `Lane ${lane}`,
        allocations: signalUsage[lane]
      }));

      setAnalyticsData({
        avgCountData,
        densityData,
        historyData,
        signalUsageData,
      });
      setLoading(false);
    } catch (err) {
      setError(err.message || 'Failed to fetch analytics data.');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000); // 4-second refresh
    return () => clearInterval(interval);
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={fetchData} />;

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem', fontWeight: '700' }}>Traffic Analytics</h2>

      <div className="grid-2">
        {/* Bar Chart: Vehicle Count per Lane */}
        <div className="card chart-card">
          <h3 className="chart-title">Average Vehicle Count per Lane</h3>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={analyticsData.avgCountData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="avg" fill="#0284c7" radius={[4, 4, 0, 0]} name="Avg Vehicles" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pie Chart: Density Distribution */}
        <div className="card chart-card">
          <h3 className="chart-title">Traffic Density Distribution</h3>
          <div style={{ width: '100%', height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ResponsiveContainer width="60%" height="100%">
              <PieChart>
                <Pie
                  data={analyticsData.densityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {analyticsData.densityData.map((entry, index) => {
                    // Match color to density label
                    const labelIdx = ['Low', 'Medium', 'High', 'Very High'].indexOf(entry.name);
                    return <Cell key={`cell-${index}`} fill={PIE_COLORS[labelIdx !== -1 ? labelIdx : 0]} />;
                  })}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            {/* Custom Legend */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem', fontWeight: '600' }}>
              {analyticsData.densityData.map((d, index) => {
                const labelIdx = ['Low', 'Medium', 'High', 'Very High'].indexOf(d.name);
                const color = PIE_COLORS[labelIdx !== -1 ? labelIdx : 0];
                return (
                  <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: color, display: 'inline-block' }}></span>
                    <span>{d.name}: {d.value} logs</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        {/* Line Chart: Historical Traffic Counts */}
        <div className="card chart-card">
          <h3 className="chart-title">Historical Traffic Timeline</h3>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <LineChart data={analyticsData.historyData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="A" stroke="#3b82f6" activeDot={{ r: 8 }} name="Lane A" strokeWidth={2} />
                <Line type="monotone" dataKey="B" stroke="#10b981" name="Lane B" strokeWidth={2} />
                <Line type="monotone" dataKey="C" stroke="#ef4444" name="Lane C" strokeWidth={2} />
                <Line type="monotone" dataKey="D" stroke="#f59e0b" name="Lane D" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bar Chart: Signal Allocations */}
        <div className="card chart-card">
          <h3 className="chart-title">Green Signal Allocations</h3>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={analyticsData.signalUsageData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="allocations" fill="#a855f7" radius={[4, 4, 0, 0]} name="Cycles Scheduled" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

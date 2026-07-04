import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { fetchAnalytics } from '../services/api';

export default function Analytics() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchAnalytics().then(setData).catch(console.error);
  }, []);

  const chartData = (data?.hourlyTraffic ?? []).map((h) => ({
    hour: `${h._id}:00`,
    vehicles: h.count,
  }));

  return (
    <div>
      <h2>Analytics</h2>
      <div className="chart-container">
        <h3>Hourly Traffic</h3>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="vehicles" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="empty">No traffic data available yet.</p>
        )}
      </div>
    </div>
  );
}

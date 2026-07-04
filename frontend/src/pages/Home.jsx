import { useEffect, useState } from 'react';
import StatCard from '../components/StatCard';
import { fetchAnalytics, fetchAccidents } from '../services/api';

export default function Home() {
  const [data, setData] = useState(null);
  const [accidents, setAccidents] = useState([]);

  useEffect(() => {
    Promise.all([fetchAnalytics(), fetchAccidents()])
      .then(([analytics, accidentList]) => {
        setData(analytics);
        setAccidents(accidentList);
      })
      .catch(console.error);
  }, []);

  const todayAccidents = accidents.filter(
    (a) => new Date(a.createdAt).toDateString() === new Date().toDateString()
  ).length;

  return (
    <div>
      <h2>Dashboard Overview</h2>
      <div className="grid">
        <StatCard title="Total Vehicles" value={data?.totalVehicles ?? '—'} />
        <StatCard title="Average Wait Time" value={data ? `${data.averageWaitTimeSec}s` : '—'} />
        <StatCard title="Accidents Today" value={todayAccidents} />
        <StatCard title="Active Signals" value={data?.signals?.length ?? '—'} />
      </div>
    </div>
  );
}

import { useEffect, useState } from 'react';
import { fetchAccidents } from '../services/api';

export default function AccidentReports() {
  const [accidents, setAccidents] = useState([]);

  useEffect(() => {
    fetchAccidents().then(setAccidents).catch(console.error);
  }, []);

  return (
    <div>
      <h2>Accident Reports</h2>
      {accidents.length === 0 ? (
        <p className="empty">No accidents reported.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Location</th>
              <th>Status</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {accidents.map((a) => (
              <tr key={a._id}>
                <td>{a.type}</td>
                <td>{a.location}</td>
                <td>{a.status}</td>
                <td>{new Date(a.createdAt).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

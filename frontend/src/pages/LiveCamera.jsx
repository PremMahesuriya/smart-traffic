import { useEffect, useState } from 'react';
import { fetchCameras } from '../services/api';

export default function LiveCamera() {
  const [cameras, setCameras] = useState([]);

  useEffect(() => {
    fetchCameras().then(setCameras).catch(console.error);
  }, []);

  return (
    <div>
      <h2>Live Camera Feeds</h2>
      {cameras.length === 0 ? (
        <p className="empty">No cameras configured. Add cameras via the Admin Panel or API.</p>
      ) : (
        <div className="grid">
          {cameras.map((cam) => (
            <div key={cam._id} className="camera-card">
              <h3>{cam.name}</h3>
              <p>{cam.location}</p>
              <span className={`badge ${cam.status}`}>{cam.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

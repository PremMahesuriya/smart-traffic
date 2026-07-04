const API_BASE = '/api';

export async function fetchTraffic() {
  const res = await fetch(`${API_BASE}/traffic`);
  if (!res.ok) throw new Error('Failed to fetch traffic');
  return res.json();
}

export async function fetchSignals() {
  const res = await fetch(`${API_BASE}/signals`);
  if (!res.ok) throw new Error('Failed to fetch signals');
  return res.json();
}

export async function fetchAnalytics() {
  const res = await fetch(`${API_BASE}/analytics`);
  if (!res.ok) throw new Error('Failed to fetch analytics');
  return res.json();
}

export async function fetchCameras() {
  const res = await fetch(`${API_BASE}/cameras`);
  if (!res.ok) throw new Error('Failed to fetch cameras');
  return res.json();
}

export async function fetchAccidents() {
  const res = await fetch(`${API_BASE}/accidents`);
  if (!res.ok) throw new Error('Failed to fetch accidents');
  return res.json();
}

export async function updateSignal(data) {
  const res = await fetch(`${API_BASE}/signal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to update signal');
  return res.json();
}

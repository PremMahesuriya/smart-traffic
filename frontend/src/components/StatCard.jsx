export default function StatCard({ title, value, color }) {
  return (
    <div className="card stat-card" style={{ borderLeft: color ? `4px solid ${color}` : undefined }}>
      <span className="stat-title">{title}</span>
      <span className="stat-value">{value}</span>
    </div>
  );
}

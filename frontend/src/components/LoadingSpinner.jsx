export default function LoadingSpinner() {
  return (
    <div className="spinner-container">
      <div className="spinner"></div>
      <p style={{ color: '#64748b', fontWeight: '500' }}>Fetching real-time traffic statistics...</p>
    </div>
  );
}

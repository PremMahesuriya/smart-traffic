export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="error-container">
      <div>
        <h4 style={{ fontWeight: '700', marginBottom: '0.25rem' }}>Connection Failure</h4>
        <p style={{ fontSize: '0.95rem' }}>{message || 'Unable to retrieve data from REST endpoints. Please check database status.'}</p>
      </div>
      {onRetry && (
        <button className="retry-btn" onClick={onRetry}>
          Retry Request
        </button>
      )}
    </div>
  );
}

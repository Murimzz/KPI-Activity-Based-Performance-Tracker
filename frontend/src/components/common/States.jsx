export default function LoadingState({ label = 'Loading…' }) {
  return (
    <div className="state-box" role="status">
      <div className="spinner-border text-primary" />
      <p className="mb-0 mt-2">{label}</p>
    </div>
  );
}

export function EmptyState({ title, message }) {
  return (
    <div className="state-box empty">
      <h2 className="h5 mb-1">{title}</h2>
      <p className="mb-0 text-muted">{message}</p>
    </div>
  );
}

export function ErrorState({ message }) {
  return (
    <div className="alert alert-danger" role="alert">
      {message}
    </div>
  );
}

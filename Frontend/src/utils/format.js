export function generateCaseId(existingCount) {
  const year = new Date().getFullYear();
  const n = String(existingCount + 1).padStart(6, '0');
  return `FIS-${year}-${n}`;
}

export function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatDateShort(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

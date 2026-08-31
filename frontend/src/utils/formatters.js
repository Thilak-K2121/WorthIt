export function formatCurrency(amount, currency = 'INR') {
  if (amount == null) return 'N/A';
  if (currency === 'INR') {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency || 'USD',
    maximumFractionDigits: 0
  }).format(amount);
}

export function formatDate(dateString) {
  if (!dateString) return 'N/A';
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch {
    return dateString;
  }
}

export function getConfidenceBadgeClass(level) {
  switch (level) {
    case 'HIGH':
      return 'bg-emerald-50 text-emerald-800 border-emerald-200';
    case 'MODERATE':
      return 'bg-teal-50 text-teal-800 border-teal-200';
    case 'LOW':
      return 'bg-amber-50 text-amber-800 border-amber-200';
    case 'VERY_LOW':
    default:
      return 'bg-rose-50 text-rose-800 border-rose-200';
  }
}

export function getScoreColor(score) {
  if (score == null) return 'text-slate-400';
  if (score >= 4.3) return 'text-emerald-600';
  if (score >= 3.8) return 'text-teal-600';
  if (score >= 3.0) return 'text-amber-600';
  return 'text-rose-600';
}

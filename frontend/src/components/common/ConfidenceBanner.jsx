import React from 'react';
import { AlertCircle, CheckCircle2, Info, AlertTriangle } from 'lucide-react';
import { getConfidenceBadgeClass } from '../../utils/formatters';

export default function ConfidenceBanner({ confidence }) {
  if (!confidence) return null;

  const getIcon = () => {
    switch (confidence.confidence_level) {
      case 'HIGH':
        return <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />;
      case 'MODERATE':
        return <Info className="w-5 h-5 text-teal-600 shrink-0" />;
      case 'LOW':
        return <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />;
      case 'VERY_LOW':
      case 'NONE':
      default:
        return <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />;
    }
  };

  return (
    <div className={`p-4 rounded-xl border flex items-start gap-3.5 shadow-sm ${getConfidenceBadgeClass(confidence.confidence_level)}`}>
      {getIcon()}
      <div>
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-bold text-sm">
            {confidence.badge_label}
          </span>
          {confidence.is_authoritative ? (
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold border border-emerald-300">
              Statistically Significant
            </span>
          ) : (
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold border border-amber-300">
              Directional Sample Only
            </span>
          )}
        </div>
        <p className="text-xs mt-1 leading-relaxed opacity-90">
          {confidence.explanation}
        </p>
      </div>
    </div>
  );
}

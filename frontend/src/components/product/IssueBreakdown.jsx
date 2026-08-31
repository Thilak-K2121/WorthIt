import React from 'react';
import { AlertTriangle, Wrench, ShieldAlert } from 'lucide-react';

export default function IssueBreakdown({ issues }) {
  if (!issues || issues.length === 0) {
    return (
      <div className="p-6 text-center bg-white rounded-3xl border border-slate-200 shadow-sm">
        <p className="text-xs text-slate-500">
          No hardware or software failure patterns reported by owners yet.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-500" />
            Reported Hardware & Software Issues
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Structured problem taxonomy aggregated across owner reports. (Distinguished from laboratory failure rates).
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {issues.map((iss, idx) => (
          <div key={idx} className="bg-white rounded-2xl p-4 border border-slate-200 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-sm text-slate-900 capitalize">
                  {iss.category_name}
                </span>
                <span className={`text-xs font-black px-2.5 py-0.5 rounded-full ${
                  iss.percentage_of_owners > 15
                    ? 'bg-rose-50 text-rose-700 border border-rose-200'
                    : iss.percentage_of_owners > 8
                    ? 'bg-amber-50 text-amber-700 border border-amber-200'
                    : 'bg-slate-100 text-slate-700 border border-slate-200'
                }`}>
                  {iss.percentage_of_owners}% of owners
                </span>
              </div>

              {iss.most_common_complaint && (
                <p className="text-xs text-slate-600 line-clamp-2 mt-1 leading-relaxed">
                  "{iss.most_common_complaint}"
                </p>
              )}
            </div>

            <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
              <span>Avg month: <strong className="text-slate-800 font-semibold">{iss.average_occurred_month || 'N/A'}</strong></span>
              {iss.repair_required_count > 0 && (
                <span className="text-amber-700 flex items-center gap-1 font-bold">
                  <Wrench className="w-3 h-3" />
                  {iss.repair_required_count} required repair
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

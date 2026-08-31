import React from 'react';
import { Clock, Star, ThumbsUp, ThumbsDown, Wrench } from 'lucide-react';
import { formatDate, getScoreColor, formatCurrency } from '../../utils/formatters';

export default function ExperienceReportCard({ report }) {
  if (!report) return null;

  return (
    <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
      {/* Header with Duration & Trust badge */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2.5">
          <div className="px-3 py-1 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-emerald-600" />
            {report.ownership_duration_months} Months of Ownership
          </div>
          <span className="text-xs text-slate-400">
            {formatDate(report.report_date)} (v{report.report_version})
          </span>
        </div>

        <div className="flex items-center gap-2">
          {report.would_buy_again === 'YES' ? (
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold border border-emerald-200 flex items-center gap-1">
              <ThumbsUp className="w-3 h-3 text-emerald-600" /> Would Buy Again
            </span>
          ) : report.would_buy_again === 'NO' ? (
            <span className="px-2.5 py-0.5 rounded-full bg-rose-100 text-rose-800 text-xs font-bold border border-rose-200 flex items-center gap-1">
              <ThumbsDown className="w-3 h-3 text-rose-600" /> Would Not Buy
            </span>
          ) : (
            <span className="px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 text-xs font-bold border border-amber-200">
              Unsure
            </span>
          )}

          <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200 font-medium">
            {report.trust_status.replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Ratings Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-2 bg-slate-50 p-3.5 rounded-2xl border border-slate-200/70 text-xs">
        <div>
          <span className="text-slate-500 block text-[11px] font-semibold uppercase tracking-wider">Overall</span>
          <span className={`font-black text-base ${getScoreColor(Number(report.overall_satisfaction))}`}>
            {Number(report.overall_satisfaction).toFixed(1)} / 5.0
          </span>
        </div>
        <div>
          <span className="text-slate-500 block text-[11px] font-semibold uppercase tracking-wider">Battery</span>
          <span className={`font-black text-base ${getScoreColor(Number(report.battery_satisfaction))}`}>
            {Number(report.battery_satisfaction).toFixed(1)} / 5.0
          </span>
        </div>
        {report.camera_satisfaction && (
          <div>
            <span className="text-slate-500 block text-[11px] font-semibold uppercase tracking-wider">Camera</span>
            <span className={`font-black text-base ${getScoreColor(Number(report.camera_satisfaction))}`}>
              {Number(report.camera_satisfaction).toFixed(1)} / 5.0
            </span>
          </div>
        )}
        <div>
          <span className="text-slate-500 block text-[11px] font-semibold uppercase tracking-wider">Performance</span>
          <span className={`font-black text-base ${getScoreColor(Number(report.performance_satisfaction))}`}>
            {Number(report.performance_satisfaction).toFixed(1)} / 5.0
          </span>
        </div>
        <div>
          <span className="text-slate-500 block text-[11px] font-semibold uppercase tracking-wider">Software</span>
          <span className={`font-black text-base ${getScoreColor(Number(report.software_satisfaction))}`}>
            {Number(report.software_satisfaction).toFixed(1)} / 5.0
          </span>
        </div>
      </div>

      {/* Longitudinal Nuances */}
      <div className="flex items-center gap-2 flex-wrap text-xs text-slate-600">
        {report.battery_degradation_perception && (
          <span className="px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200">
            Battery Degradation: <strong className="text-slate-900">{report.battery_degradation_perception}</strong>
          </span>
        )}
        {report.heating_experience && (
          <span className="px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200">
            Heating: <strong className="text-slate-900">{report.heating_experience.replace('_', ' ')}</strong>
          </span>
        )}
        {report.software_update_experience && (
          <span className="px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200">
            Update Stability: <strong className="text-emerald-700">{report.software_update_experience}</strong>
          </span>
        )}
      </div>

      {/* Positives & Problems */}
      <div className="space-y-2 text-xs">
        {report.biggest_positive && (
          <div className="p-3 rounded-2xl bg-emerald-50/70 border border-emerald-200 text-slate-800 leading-relaxed">
            <span className="font-bold text-emerald-800 block mb-0.5">Top Positive:</span>
            {report.biggest_positive}
          </div>
        )}
        {report.biggest_problem && (
          <div className="p-3 rounded-2xl bg-rose-50/70 border border-rose-200 text-slate-800 leading-relaxed">
            <span className="font-bold text-rose-800 block mb-0.5">Top Complaint:</span>
            {report.biggest_problem}
          </div>
        )}
      </div>

      {/* Issues / Repairs Attached */}
      {report.repairs && report.repairs.length > 0 && (
        <div className="pt-2 border-t border-slate-100">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1.5 flex items-center gap-1">
            <Wrench className="w-3 h-3 text-emerald-600" /> Repair History
          </span>
          <div className="space-y-1.5">
            {report.repairs.map((r, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                <span className="text-slate-700 font-medium">Replaced {r.part_replaced} ({r.official_service_center ? 'Official Service Center' : 'Third-Party'})</span>
                <span className="font-mono text-emerald-700 font-bold">{formatCurrency(r.cost, r.currency)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

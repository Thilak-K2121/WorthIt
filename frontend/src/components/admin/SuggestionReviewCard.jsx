import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle2, Pencil, ArrowRight } from 'lucide-react';

const inputCls =
  'w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 text-sm font-semibold focus:outline-none focus:border-[#00D09C] focus:bg-white transition-colors';

/**
 * One user suggestion in the moderation queue.
 * Pending: the admin can correct brand / model / variant before approving.
 * Approved: links to the catalog entry; later renames happen in the Catalog Manager.
 */
export default function SuggestionReviewCard({ suggestion: s, onReview, onOpenCatalogManager }) {
  const [brand, setBrand] = useState(s.brand);
  const [model, setModel] = useState(s.model_name);
  const [variant, setVariant] = useState(s.variant_details || '');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const edited = brand.trim() !== s.brand || model.trim() !== s.model_name || variant.trim() !== (s.variant_details || '');
  const isPending = s.status === 'PENDING';

  const submit = async (action) => {
    setBusy(true);
    setError('');
    try {
      const payload = { action };
      if (action === 'APPROVE') {
        payload.brand = brand.trim();
        payload.model_name = model.trim();
        payload.variant_details = variant.trim();
      }
      await onReview(s.id, payload);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const statusCls =
    s.status === 'APPROVED' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
      : s.status === 'PENDING' ? 'bg-amber-50 text-amber-800 border border-amber-200'
      : 'bg-slate-100 text-slate-600';

  return (
    <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4 flex flex-col justify-between">
      <div className="space-y-3">
        <div className="flex items-center justify-between gap-2">
          {isPending ? (
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Pencil className="w-3 h-3" /> Review &amp; correct before publishing
            </span>
          ) : (
            <span className="text-xs uppercase font-extrabold text-emerald-700">{s.brand}</span>
          )}
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold shrink-0 ${statusCls}`}>{s.status}</span>
        </div>

        {isPending ? (
          <div className="space-y-2">
            <div className="grid grid-cols-[1fr_2fr] gap-2">
              <label className="space-y-1">
                <span className="text-[10px] font-bold uppercase text-slate-400">Brand</span>
                <input value={brand} onChange={(e) => setBrand(e.target.value)} className={inputCls} />
              </label>
              <label className="space-y-1">
                <span className="text-[10px] font-bold uppercase text-slate-400">Model</span>
                <input value={model} onChange={(e) => setModel(e.target.value)} className={inputCls} />
              </label>
            </div>
            <label className="space-y-1 block">
              <span className="text-[10px] font-bold uppercase text-slate-400">Variant (RAM / storage)</span>
              <input value={variant} onChange={(e) => setVariant(e.target.value)} placeholder="8GB / 256GB" className={inputCls} />
            </label>
            {edited && (
              <p className="text-[11px] text-slate-400">
                User submitted: <span className="font-semibold text-slate-500">{s.brand} {s.model_name}{s.variant_details ? ` · ${s.variant_details}` : ''}</span>
              </p>
            )}
          </div>
        ) : (
          <>
            <h4 className="text-xl font-black text-slate-900">{s.model_name}</h4>
            {s.variant_details && <p className="text-xs text-slate-600 font-medium">Variant: {s.variant_details}</p>}
          </>
        )}

        {s.notes && (
          <p className="text-xs text-slate-500 italic bg-slate-50 p-2.5 rounded-xl border border-slate-100">"{s.notes}"</p>
        )}
        {error && (
          <p className="text-xs font-semibold text-rose-700 bg-rose-50 border border-rose-200 rounded-xl p-2.5">{error}</p>
        )}
      </div>

      {isPending ? (
        <div className="flex items-center gap-2 pt-3 border-t border-slate-100">
          <button
            onClick={() => submit('APPROVE')}
            disabled={busy || !brand.trim() || !model.trim()}
            className="flex-1 py-2.5 rounded-xl btn-lexi-mint text-xs font-bold flex items-center justify-center gap-1.5 disabled:opacity-50"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>{busy ? 'Publishing…' : edited ? 'Approve with edits' : 'Approve & publish'}</span>
          </button>
          <button
            onClick={() => submit('REJECT')}
            disabled={busy}
            className="px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors disabled:opacity-50"
          >
            Reject
          </button>
        </div>
      ) : (
        <div className="pt-2 border-t border-slate-100 flex items-center justify-between gap-2 text-xs">
          {s.status === 'APPROVED' && s.target_product_id ? (
            <>
              <button
                onClick={onOpenCatalogManager}
                className="text-slate-500 hover:text-emerald-700 font-bold flex items-center gap-1"
              >
                <Pencil className="w-3 h-3" /> Rename in Catalog Manager
              </button>
              <Link to={`/products/${s.target_product_id}`} className="text-emerald-700 font-bold flex items-center gap-1 hover:underline">
                View <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </>
          ) : (
            <span className="text-slate-400 font-medium">Reviewed</span>
          )}
        </div>
      )}
    </div>
  );
}

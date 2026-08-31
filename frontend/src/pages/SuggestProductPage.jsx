import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { HelpCircle, Send, CheckCircle2, AlertCircle, ChevronDown, ChevronUp, Sparkles, Smartphone } from 'lucide-react';
import { api } from '../services/api';

const POPULAR_BRANDS = ['Apple', 'Samsung', 'Google', 'OnePlus', 'Motorola', 'Nothing', 'Xiaomi', 'Other'];

export default function SuggestProductPage() {
  const [searchParams] = useSearchParams();
  const prefillBrand = searchParams.get('brand') || '';

  const [selectedBrand, setSelectedBrand] = useState(prefillBrand || 'Motorola');
  const [customBrand, setCustomBrand] = useState('');
  const [modelName, setModelName] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [variantDetails, setVariantDetails] = useState('');
  const [officialUrl, setOfficialUrl] = useState('');
  const [notes, setNotes] = useState('');

  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (prefillBrand) {
      if (POPULAR_BRANDS.includes(prefillBrand)) {
        setSelectedBrand(prefillBrand);
      } else {
        setSelectedBrand('Other');
        setCustomBrand(prefillBrand);
      }
    }
  }, [prefillBrand]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const finalBrand = selectedBrand === 'Other' ? customBrand.trim() : selectedBrand;
    if (!finalBrand) {
      setError('Please specify a brand.');
      return;
    }
    if (!modelName.trim()) {
      setError('Please enter the model name.');
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const res = await api.submitSuggestion({
        brand: finalBrand,
        model_name: modelName.trim(),
        variant_details: variantDetails.trim() || undefined,
        official_url: officialUrl.trim() || undefined,
        notes: notes.trim() || undefined
      });
      setResult(res);
    } catch (err) {
      setError(err.message || 'Failed to submit suggestion.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="py-10 max-w-xl mx-auto space-y-8">
      {/* Header with Pop-In */}
      <div className="text-center space-y-3 hero-animate-title">
        <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-[#00D09C] flex items-center justify-center mx-auto shadow-sm">
          <HelpCircle className="w-6 h-6" strokeWidth={2.5} />
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
          Request a Missing Phone
        </h1>
        <p className="text-sm text-slate-500 max-w-md mx-auto leading-relaxed hero-animate-subtitle">
          Can't find your smartphone? Submit it in seconds and our pipeline will verify and catalog it.
        </p>
      </div>

      {result ? (
        /* Success Screen */
        <div className="p-8 sm:p-10 rounded-3xl bg-white border border-slate-200 text-center space-y-5 shadow-sm animate-fade-in-up">
          <div className="w-16 h-16 rounded-2xl bg-emerald-50 text-[#00D09C] flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-9 h-9" />
          </div>
          <div className="space-y-1.5">
            <h3 className="text-2xl font-black text-slate-900">
              {result.status === 'DUPLICATE' ? 'Device Already Cataloged!' : 'Suggestion Submitted!'}
            </h3>
            <p className="text-xs text-slate-600 max-w-sm mx-auto leading-relaxed">
              {result.status === 'DUPLICATE'
                ? 'We found this exact phone already active in our longitudinal catalog.'
                : 'Your suggestion is queued for instant catalog indexing.'}
            </p>
          </div>

          <div className="pt-3 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              to="/products"
              className="w-full sm:w-auto px-6 py-3 rounded-xl btn-lexi-mint text-xs font-bold"
            >
              Explore Device Catalog
            </Link>
            <button
              onClick={() => {
                setResult(null);
                setModelName('');
                setVariantDetails('');
              }}
              className="w-full sm:w-auto px-5 py-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors"
            >
              Suggest Another Phone
            </button>
          </div>
        </div>
      ) : (
        /* Streamlined Minimalist Submission Card (Zero Cognitive Overload) */
        <form onSubmit={handleSubmit} className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6 hero-animate-cards">
          {error && (
            <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* 1. Quick Brand Pills */}
          <div>
            <label className="text-xs font-extrabold uppercase tracking-wider text-slate-500 block mb-2.5">
              1. Select Brand
            </label>
            <div className="grid grid-cols-4 gap-2">
              {POPULAR_BRANDS.map(b => (
                <button
                  type="button"
                  key={b}
                  onClick={() => setSelectedBrand(b)}
                  className={`py-2.5 px-2 rounded-xl text-xs font-bold transition-all text-center ${
                    selectedBrand === b
                      ? 'bg-[#00D09C] text-white shadow-mint font-extrabold'
                      : 'bg-slate-50 text-slate-700 border border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {b}
                </button>
              ))}
            </div>

            {selectedBrand === 'Other' && (
              <input
                type="text"
                placeholder="Enter manufacturer name (e.g. Vivo, Realme, Asus)..."
                value={customBrand}
                onChange={(e) => setCustomBrand(e.target.value)}
                className="w-full mt-2.5 px-4 py-3 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 text-sm focus:outline-none focus:border-[#00D09C] focus:bg-white"
                required
              />
            )}
          </div>

          {/* 2. Model Name Input */}
          <div>
            <label className="text-xs font-extrabold uppercase tracking-wider text-slate-500 block mb-1.5">
              2. Smartphone Model Name *
            </label>
            <input
              type="text"
              placeholder={`e.g. ${selectedBrand === 'Apple' ? 'iPhone 16 Pro' : selectedBrand === 'Samsung' ? 'Galaxy S24 Ultra' : 'Edge 50 Pro'}`}
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              className="w-full px-4 py-3.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 text-sm font-medium focus:outline-none focus:border-[#00D09C] focus:bg-white transition-colors"
              required
            />
          </div>

          {/* 3. Optional Advanced Details Toggle (Keeps interface clean by default) */}
          <div className="pt-1">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-emerald-700 transition-colors"
            >
              <span>{showAdvanced ? 'Hide Additional Specs' : '+ Add Variant, RAM / Storage (Optional)'}</span>
              {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>

            {showAdvanced && (
              <div className="mt-3.5 space-y-3.5 pt-3 border-t border-slate-100 animate-fade-in-up">
                <div>
                  <label className="text-[11px] font-bold text-slate-600 block mb-1">
                    Variant / Storage (Optional)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. 12GB RAM / 256GB Storage"
                    value={variantDetails}
                    onChange={(e) => setVariantDetails(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 text-xs focus:outline-none focus:border-[#00D09C]"
                  />
                </div>

                <div>
                  <label className="text-[11px] font-bold text-slate-600 block mb-1">
                    Official URL or Launch Notes (Optional)
                  </label>
                  <input
                    type="text"
                    placeholder="https://... or launch market details"
                    value={officialUrl}
                    onChange={(e) => setOfficialUrl(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 text-xs focus:outline-none focus:border-[#00D09C]"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={submitting}
            className="w-full py-4 rounded-xl btn-lexi-mint font-extrabold text-sm flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
            <span>{submitting ? 'Submitting...' : 'Submit Smartphone Model'}</span>
          </button>
        </form>
      )}
    </div>
  );
}

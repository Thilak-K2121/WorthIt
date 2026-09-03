// ==============================================================================
// Ownership Intake Form - 3-Step Longitudinal Review Wizard
// ==============================================================================
// This component provides a multi-step user experience intake wizard:
// Step 1: Device Model Selection & Purchase Price
// Step 2: Longitudinal Duration (3, 6, 12, 24 months) & Multi-Category Ratings
// Step 3: Battery Degradation Perception, Written Notes, and Repurchase Verdict
// ==============================================================================

import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  Smartphone, Battery, Award, ThumbsUp, ThumbsDown, 
  HelpCircle, ArrowRight, ArrowLeft, CheckCircle2, AlertCircle, Camera, ShieldCheck,
  AlertTriangle, Wrench, ShieldAlert
} from 'lucide-react';

/**
 * 3-Step Longitudinal Ownership Form Component.
 * 
 * @param {Array} products - Available smartphone models for dropdown selection.
 * @param {Function} onSubmit - Callback function receiving the formatted JSON payload.
 * @param {boolean} isSubmitting - Loading state flag during async API submission.
 * @param {string} requestedBrand - Pre-selected brand query parameter (e.g. 'Vivo').
 * @param {string} requestedProductId - Pre-selected smartphone UUID query parameter.
 */
export default function OwnershipForm({ products, onSubmit, isSubmitting, requestedBrand, requestedProductId }) {
  const [step, setStep] = useState(1);

  // Form State: Captures device selection, ownership duration, ratings, and feedback
  const [formData, setFormData] = useState({
    product_id: requestedProductId || '',
    purchase_price: '',
    ownership_duration_months: 12,
    overall_satisfaction: '4.5',
    battery_satisfaction: '4.0',
    camera_satisfaction: '4.5',
    software_satisfaction: '4.5',
    battery_degradation_perception: 'MINOR',
    would_buy_again: 'YES',
    biggest_positive: '',
    biggest_problem: ''
  });

  // Specific Hardware Issue & Repair State
  const [hasIssues, setHasIssues] = useState(false);
  const [issueCategory, setIssueCategory] = useState('display');
  const [issueTitle, setIssueTitle] = useState('');
  const [occurredAtMonth, setOccurredAtMonth] = useState(6);
  const [repairRequired, setRepairRequired] = useState(false);
  const [repairPart, setRepairPart] = useState('SCREEN');
  const [repairCost, setRepairCost] = useState('');
  const [officialServiceCenter, setOfficialServiceCenter] = useState(true);

  const matchingBrandProducts = requestedBrand
    ? products.filter(p => p.brand.toLowerCase() === requestedBrand.toLowerCase())
    : [];

  useEffect(() => {
    if (requestedProductId) {
      setFormData(prev => ({ ...prev, product_id: requestedProductId }));
    } else if (products && products.length > 0 && !formData.product_id) {
      if (matchingBrandProducts.length > 0) {
        setFormData(prev => ({ ...prev, product_id: matchingBrandProducts[0].id }));
      } else {
        setFormData(prev => ({ ...prev, product_id: products[0].id }));
      }
    }
  }, [products, requestedBrand, requestedProductId]);

  const handleNext = () => setStep(prev => Math.min(prev + 1, 3));
  const handleBack = () => setStep(prev => Math.max(prev - 1, 1));

  const handleSubmit = (e) => {
    e.preventDefault();
    const purchaseDate = new Date(Date.now() - formData.ownership_duration_months * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    const payload = {
      product_id: formData.product_id,
      purchase_date: purchaseDate,
      ownership_start_date: purchaseDate,
      purchase_price: formData.purchase_price ? parseFloat(formData.purchase_price) : undefined,
      purchase_country: 'India',
      status: 'CURRENTLY_OWNING',
      initial_report: {
        ownership_duration_months: parseInt(formData.ownership_duration_months),
        overall_satisfaction: parseFloat(formData.overall_satisfaction),
        battery_satisfaction: parseFloat(formData.battery_satisfaction),
        camera_satisfaction: parseFloat(formData.camera_satisfaction),
        performance_satisfaction: parseFloat(formData.overall_satisfaction),
        software_satisfaction: parseFloat(formData.software_satisfaction),
        battery_degradation_perception: formData.battery_degradation_perception,
        would_buy_again: formData.would_buy_again,
        biggest_positive: formData.biggest_positive || undefined,
        biggest_problem: formData.biggest_problem || undefined,
        issues: hasIssues && issueCategory ? [{
          category_slug: issueCategory,
          issue_title: issueTitle.trim() || `${issueCategory.charAt(0).toUpperCase() + issueCategory.slice(1)} hardware or software issue`,
          severity: 'MODERATE',
          occurred_at_month: occurredAtMonth ? parseInt(occurredAtMonth) : undefined,
          repair_required: repairRequired,
          resolved: true
        }] : undefined,
        repairs: hasIssues && repairRequired ? [{
          part_replaced: repairPart || 'SCREEN',
          cost: repairCost ? parseFloat(repairCost) : 0,
          official_service_center: officialServiceCenter,
          covered_under_warranty: !repairCost || parseFloat(repairCost) === 0,
          currency: 'INR'
        }] : undefined
      }
    };
    onSubmit(payload);
  };

  return (
    <div className="bg-white rounded-3xl p-6 sm:p-10 border border-slate-200 shadow-sm space-y-8 max-w-2xl mx-auto">
      {/* Clean 3-Step Wizard Indicator */}
      <div className="space-y-3">
        <div className="flex items-center justify-between text-xs font-bold text-slate-500">
          <span className={step >= 1 ? 'text-emerald-700 font-extrabold' : ''}>
            1. Select Device
          </span>
          <span className={step >= 2 ? 'text-emerald-700 font-extrabold' : ''}>
            2. Ratings & Experience
          </span>
          <span className={step >= 3 ? 'text-emerald-700 font-extrabold' : ''}>
            3. Final Verdict
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-[#00D09C] transition-all duration-300 ease-out"
            style={{ width: `${(step / 3) * 100}%` }}
          />
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* STEP 1: Phone & Ownership Duration */}
        {step === 1 && (
          <div className="space-y-6 animate-fade-in-up">
            {/* If requested brand has no model yet, show friendly prompt */}
            {requestedBrand && matchingBrandProducts.length === 0 && (
              <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-800 text-xs flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 text-amber-600" />
                  <span>No <strong>{requestedBrand}</strong> model in database yet. Suggest your exact model to create it:</span>
                </div>
                <Link
                  to={`/suggest?brand=${encodeURIComponent(requestedBrand)}`}
                  className="px-3 py-1.5 rounded-xl bg-amber-600 text-white font-bold hover:bg-amber-700 shrink-0"
                >
                  Suggest Model
                </Link>
              </div>
            )}

            <div>
              <label className="text-sm font-bold text-slate-900 block mb-2">
                Which smartphone do you own? *
              </label>
              <select
                value={formData.product_id}
                onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
                className="w-full px-4 py-3.5 rounded-2xl bg-slate-50 border border-slate-300 text-slate-900 text-sm font-medium focus:outline-none focus:border-[#00D09C] focus:bg-white"
                required
              >
                <option value="" disabled>Select your smartphone model...</option>
                {products.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.brand} — {p.model_name}
                  </option>
                ))}
              </select>

              <div className="pt-2 text-right">
                <Link
                  to={`/suggest${requestedBrand ? `?brand=${encodeURIComponent(requestedBrand)}` : ''}`}
                  className="text-xs font-bold text-slate-500 hover:text-emerald-700 transition-colors"
                >
                  Can't find your phone? Request it here →
                </Link>
              </div>
            </div>

            <div>
              <label className="text-sm font-bold text-slate-900 block mb-2">
                How long have you owned it? *
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                {[
                  { label: '3 Months', val: 3 },
                  { label: '6 Months', val: 6 },
                  { label: '1 Year (12m)', val: 12 },
                  { label: '2+ Years (24m)', val: 24 }
                ].map(item => (
                  <button
                    type="button"
                    key={item.val}
                    onClick={() => setFormData({ ...formData, ownership_duration_months: item.val })}
                    className={`py-3 px-3 rounded-2xl border text-xs font-bold transition-all text-center ${
                      formData.ownership_duration_months === item.val
                        ? 'bg-[#00D09C] text-white border-[#00D09C] shadow-mint'
                        : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="pt-4 flex justify-end">
              <button
                type="button"
                onClick={handleNext}
                className="px-8 py-3.5 rounded-xl btn-lexi-mint font-extrabold text-sm flex items-center gap-2"
              >
                <span>Continue</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: Ratings & Experience */}
        {step === 2 && (
          <div className="space-y-6 animate-fade-in-up">
            {/* Overall Rating Slider */}
            <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-bold text-slate-900">Overall Long-Term Satisfaction</span>
                <span className="text-lg font-black text-emerald-700">{formData.overall_satisfaction} / 5.0</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="5.0"
                step="0.1"
                value={formData.overall_satisfaction}
                onChange={(e) => setFormData({ ...formData, overall_satisfaction: e.target.value })}
                className="w-full accent-[#00D09C] cursor-pointer"
              />
            </div>

            {/* Battery Health Slider */}
            <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-bold text-slate-900">Battery Endurance Today</span>
                <span className="text-lg font-black text-emerald-700">{formData.battery_satisfaction} / 5.0</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="5.0"
                step="0.1"
                value={formData.battery_satisfaction}
                onChange={(e) => setFormData({ ...formData, battery_satisfaction: e.target.value })}
                className="w-full accent-[#00D09C] cursor-pointer"
              />
            </div>

            {/* Camera Satisfaction Slider */}
            <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                  <Camera className="w-4 h-4 text-emerald-600" />
                  Camera & Photo Quality Today
                </span>
                <span className="text-lg font-black text-emerald-700">{formData.camera_satisfaction} / 5.0</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="5.0"
                step="0.1"
                value={formData.camera_satisfaction}
                onChange={(e) => setFormData({ ...formData, camera_satisfaction: e.target.value })}
                className="w-full accent-[#00D09C] cursor-pointer"
              />
            </div>

            {/* Software Experience Slider */}
            <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  Software Stability & UI Smoothness
                </span>
                <span className="text-lg font-black text-emerald-700">{formData.software_satisfaction} / 5.0</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="5.0"
                step="0.1"
                value={formData.software_satisfaction}
                onChange={(e) => setFormData({ ...formData, software_satisfaction: e.target.value })}
                className="w-full accent-[#00D09C] cursor-pointer"
              />
            </div>

            {/* Repurchase Verdict */}
            <div>
              <label className="text-sm font-bold text-slate-900 block mb-2">
                Would you buy this phone again knowing what you know now? *
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { label: 'YES — Absolutely', val: 'YES', activeClass: 'bg-emerald-50 border-emerald-300 text-emerald-800' },
                  { label: 'UNSURE — Mixed', val: 'UNSURE', activeClass: 'bg-amber-50 border-amber-300 text-amber-800' },
                  { label: 'NO — Regret it', val: 'NO', activeClass: 'bg-rose-50 border-rose-300 text-rose-800' }
                ].map(item => (
                  <button
                    type="button"
                    key={item.val}
                    onClick={() => setFormData({ ...formData, would_buy_again: item.val })}
                    className={`p-3.5 rounded-2xl border text-xs font-bold text-center transition-all ${
                      formData.would_buy_again === item.val
                        ? `${item.activeClass} ring-2 ring-emerald-400 font-black`
                        : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="pt-4 flex items-center justify-between">
              <button
                type="button"
                onClick={handleBack}
                className="px-5 py-3 rounded-xl bg-slate-100 text-slate-700 text-xs font-bold flex items-center gap-1.5 hover:bg-slate-200"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </button>

              <button
                type="button"
                onClick={handleNext}
                className="px-8 py-3.5 rounded-xl btn-lexi-mint font-extrabold text-sm flex items-center gap-2"
              >
                <span>Continue</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: Quick Highlights & Publish */}
        {step === 3 && (
          <div className="space-y-6 animate-fade-in-up">
            {/* Battery degradation perception */}
            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">
                How has battery degradation felt?
              </label>
              <div className="grid grid-cols-4 gap-2">
                {[
                  { label: 'None', val: 'NONE' },
                  { label: 'Minor', val: 'MINOR' },
                  { label: 'Moderate', val: 'MODERATE' },
                  { label: 'Severe', val: 'SEVERE' }
                ].map(b => (
                  <button
                    type="button"
                    key={b.val}
                    onClick={() => setFormData({ ...formData, battery_degradation_perception: b.val })}
                    className={`py-2.5 px-2 rounded-xl text-xs font-bold border transition-all ${
                      formData.battery_degradation_perception === b.val
                        ? 'bg-[#00D09C] text-white border-[#00D09C]'
                        : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {b.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">
                What is the #1 best thing about this phone? (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Crisp zoom camera, excellent battery life, lightweight design."
                value={formData.biggest_positive}
                onChange={(e) => setFormData({ ...formData, biggest_positive: e.target.value })}
                className="w-full px-4 py-3 rounded-2xl bg-slate-50 border border-slate-300 text-slate-900 text-sm focus:outline-none focus:border-[#00D09C] focus:bg-white"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">
                Any recurring complaint or problem? (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Mild heating when recording long 4K videos."
                value={formData.biggest_problem}
                onChange={(e) => setFormData({ ...formData, biggest_problem: e.target.value })}
                className="w-full px-4 py-3 rounded-2xl bg-slate-50 border border-slate-300 text-slate-900 text-sm focus:outline-none focus:border-[#00D09C] focus:bg-white"
              />
            </div>

            {/* Hardware & Software Issue Intake Section */}
            <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-amber-600" />
                  <span className="text-xs font-bold text-slate-900">Did you encounter any specific hardware fault or failure?</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={hasIssues}
                    onChange={(e) => setHasIssues(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#00D09C]"></div>
                </label>
              </div>

              {hasIssues && (
                <div className="space-y-4 pt-2 border-t border-slate-200 animate-fade-in-up">
                  {/* Category Selection */}
                  <div>
                    <label className="text-[11px] font-bold text-slate-600 block mb-1">
                      Fault Category
                    </label>
                    <select
                      value={issueCategory}
                      onChange={(e) => setIssueCategory(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-white border border-slate-300 text-slate-900 text-xs font-semibold focus:outline-none focus:border-[#00D09C]"
                    >
                      <option value="display">Display (Green Line / Burn-in / Touch Latency)</option>
                      <option value="battery">Battery (Rapid Drain / Swelling / Capacity Drop)</option>
                      <option value="heating">Heating / Thermal Throttling</option>
                      <option value="motherboard">Motherboard / Dead Boot / Re-balling</option>
                      <option value="charging">Charging Port / Slow Charge / Loose Cable</option>
                      <option value="camera">Camera (Autofocus / Lens Fog / Sensor Error)</option>
                      <option value="software">Software (Crash Loops / UI Stutter / Update Bugs)</option>
                      <option value="build">Build / Physical Fracture (Frame / Back Glass)</option>
                      <option value="other">Other Miscellaneous Issue</option>
                    </select>
                  </div>

                  {/* Specific Description & Month */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div className="sm:col-span-2">
                      <label className="text-[11px] font-bold text-slate-600 block mb-1">
                        Specific Symptom
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Vertical green line appeared after OTA update"
                        value={issueTitle}
                        onChange={(e) => setIssueTitle(e.target.value)}
                        className="w-full px-3.5 py-2 rounded-xl bg-white border border-slate-300 text-xs text-slate-900 focus:outline-none focus:border-[#00D09C]"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-bold text-slate-600 block mb-1">
                        Occurred At Month
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="60"
                        value={occurredAtMonth}
                        onChange={(e) => setOccurredAtMonth(e.target.value)}
                        className="w-full px-3.5 py-2 rounded-xl bg-white border border-slate-300 text-xs text-slate-900 focus:outline-none focus:border-[#00D09C]"
                      />
                    </div>
                  </div>

                  {/* Repair Sub-section */}
                  <div className="pt-2 border-t border-slate-200">
                    <label className="flex items-center gap-2 text-xs font-bold text-slate-700 cursor-pointer mb-2">
                      <input
                        type="checkbox"
                        checked={repairRequired}
                        onChange={(e) => setRepairRequired(e.target.checked)}
                        className="rounded accent-[#00D09C]"
                      />
                      <span>Did you have to get this device repaired?</span>
                    </label>

                    {repairRequired && (
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-white p-3 rounded-xl border border-slate-200 animate-fade-in-up">
                        <div>
                          <label className="text-[10px] font-bold text-slate-500 block mb-1">Part Replaced</label>
                          <select
                            value={repairPart}
                            onChange={(e) => setRepairPart(e.target.value)}
                            className="w-full p-1.5 rounded-lg bg-slate-50 border border-slate-300 text-xs text-slate-800"
                          >
                            <option value="SCREEN">Display / Screen</option>
                            <option value="BATTERY">Battery</option>
                            <option value="MOTHERBOARD">Motherboard</option>
                            <option value="CAMERA">Camera Module</option>
                            <option value="PORT">Charging Port</option>
                            <option value="BACK_GLASS">Back Glass</option>
                            <option value="OTHER">Other Part</option>
                          </select>
                        </div>
                        <div>
                          <label className="text-[10px] font-bold text-slate-500 block mb-1">Cost Paid (₹ INR)</label>
                          <input
                            type="number"
                            placeholder="0 for warranty"
                            value={repairCost}
                            onChange={(e) => setRepairCost(e.target.value)}
                            className="w-full p-1.5 rounded-lg bg-slate-50 border border-slate-300 text-xs text-slate-800"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] font-bold text-slate-500 block mb-1">Service Center</label>
                          <select
                            value={officialServiceCenter ? 'true' : 'false'}
                            onChange={(e) => setOfficialServiceCenter(e.target.value === 'true')}
                            className="w-full p-1.5 rounded-lg bg-slate-50 border border-slate-300 text-xs text-slate-800"
                          >
                            <option value="true">Official Brand Center</option>
                            <option value="false">Third-Party / Local</option>
                          </select>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="pt-4 flex items-center justify-between">
              <button
                type="button"
                onClick={handleBack}
                className="px-5 py-3 rounded-xl bg-slate-100 text-slate-700 text-xs font-bold flex items-center gap-1.5 hover:bg-slate-200"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </button>

              <button
                type="submit"
                disabled={isSubmitting}
                className="px-8 py-3.5 rounded-xl btn-lexi-mint font-extrabold text-sm disabled:opacity-50 flex items-center gap-2"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>{isSubmitting ? 'Publishing...' : 'Publish Experience Report'}</span>
              </button>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}

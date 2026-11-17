import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  KeyRound, Lock, Unlock, Plus, Trash2, Search, Database, RefreshCw, Smartphone, X, Zap, AlertTriangle,
} from 'lucide-react';
import { api, getAdminKey, setAdminKey } from '../../services/api';

const EMPTY_VARIANT = { ram: '', storage: '', chipset: '', launch_price: '' };
const EMPTY_FORM = {
  brand: '',
  model_name: '',
  release_date: '',
  country_market: 'India',
  official_url: '',
  description: '',
  variants: [{ ...EMPTY_VARIANT }],
};

const SOURCE_STYLES = {
  AUTOMATED: 'bg-purple-50 text-purple-700 border-purple-200',
  MANUAL: 'bg-slate-100 text-slate-600 border-slate-200',
  USER_SUGGESTED: 'bg-amber-50 text-amber-700 border-amber-200',
};

const inputCls =
  'w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 text-sm font-medium focus:outline-none focus:border-[#00D09C] focus:bg-white transition-colors';

export default function CatalogManager({ onCatalogChanged }) {
  // ---------------------------------------------------------------- admin key
  const [keyInput, setKeyInput] = useState('');
  const [unlocked, setUnlocked] = useState(false);
  const [keyError, setKeyError] = useState('');

  useEffect(() => {
    // Re-validate a stored key (or an open dev server with no key configured)
    api.verifyAdminKey(getAdminKey())
      .then(() => setUnlocked(true))
      .catch(() => setUnlocked(false));
  }, []);

  const handleUnlock = async (e) => {
    e.preventDefault();
    setKeyError('');
    try {
      await api.verifyAdminKey(keyInput.trim());
      setAdminKey(keyInput.trim());
      setUnlocked(true);
      setKeyInput('');
    } catch (err) {
      setKeyError(err.message);
    }
  };

  const handleLock = () => {
    setAdminKey('');
    setUnlocked(false);
  };

  // ---------------------------------------------------------------- add form
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formMsg, setFormMsg] = useState(null);

  const updateField = (field, value) => setForm((f) => ({ ...f, [field]: value }));
  const updateVariant = (idx, field, value) =>
    setForm((f) => ({
      ...f,
      variants: f.variants.map((v, i) => (i === idx ? { ...v, [field]: value } : v)),
    }));
  const addVariant = () => setForm((f) => ({ ...f, variants: [...f.variants, { ...EMPTY_VARIANT }] }));
  const removeVariant = (idx) => setForm((f) => ({ ...f, variants: f.variants.filter((_, i) => i !== idx) }));

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    setFormMsg(null);
    const variants = form.variants
      .filter((v) => v.ram || v.storage || v.chipset || v.launch_price)
      .map((v) => ({
        ram: v.ram || null,
        storage: v.storage || null,
        chipset: v.chipset || null,
        launch_price: v.launch_price ? Number(v.launch_price) : null,
        currency: 'INR',
      }));
    try {
      const created = await api.adminCreateProduct({
        brand: form.brand.trim(),
        model_name: form.model_name.trim(),
        release_date: form.release_date || null,
        country_market: form.country_market || 'Global',
        official_url: form.official_url || null,
        description: form.description || null,
        discovery_source: 'MANUAL',
        status: 'ACTIVE',
        variants,
      });
      setFormMsg({ type: 'ok', text: `Added ${created.brand} ${created.model_name}`, id: created.id });
      setForm(EMPTY_FORM);
      loadProducts();
      onCatalogChanged?.();
    } catch (err) {
      setFormMsg({ type: 'error', text: err.message });
    } finally {
      setSaving(false);
    }
  };

  // ---------------------------------------------------------------- list + delete
  const [search, setSearch] = useState('');
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [listLoading, setListLoading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  const loadProducts = async (q = search) => {
    setListLoading(true);
    try {
      const res = await api.getProducts({ search: q, sort_by: 'release_date', page_size: 100 });
      setProducts(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error('Failed to load products:', err);
    } finally {
      setListLoading(false);
    }
  };

  useEffect(() => {
    const t = setTimeout(() => loadProducts(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  const handleDelete = async (p) => {
    const ownerWarning = p.total_owners_count
      ? `\n\nThis also deletes ${p.total_owners_count} owner record(s) and their experience reports.`
      : '';
    if (!window.confirm(`Delete "${p.brand} ${p.model_name}" from the database?${ownerWarning}\n\nThis cannot be undone.`)) return;
    setDeletingId(p.id);
    try {
      await api.adminDeleteProduct(p.id);
      setProducts((list) => list.filter((x) => x.id !== p.id));
      setTotal((t) => Math.max(0, t - 1));
      onCatalogChanged?.();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  // ---------------------------------------------------------------- cache panel
  const [cacheStats, setCacheStats] = useState(null);
  const loadCacheStats = () => api.adminCacheStats().then(setCacheStats).catch(() => setCacheStats(null));
  useEffect(() => {
    if (unlocked) loadCacheStats();
  }, [unlocked]);

  const handleFlush = async () => {
    try {
      const res = await api.adminFlushCache();
      alert(`Cache cleared: ${res.keys_removed} cached responses removed.`);
      loadCacheStats();
    } catch (err) {
      alert(`Flush failed: ${err.message}`);
    }
  };

  // ---------------------------------------------------------------- render
  if (!unlocked) {
    return (
      <form
        onSubmit={handleUnlock}
        className="max-w-md mx-auto bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-4 text-center animate-fade-in-up"
      >
        <div className="w-12 h-12 rounded-xl bg-slate-100 text-slate-600 flex items-center justify-center mx-auto">
          <Lock className="w-6 h-6" />
        </div>
        <h3 className="text-base font-extrabold text-slate-900">Admin key required</h3>
        <p className="text-xs text-slate-500">
          Adding and deleting catalog entries is restricted. Enter the <code>ADMIN_API_KEY</code> configured on the backend.
        </p>
        <input
          type="password"
          value={keyInput}
          onChange={(e) => setKeyInput(e.target.value)}
          placeholder="Admin key"
          autoComplete="current-password"
          className={inputCls}
        />
        {keyError && <p className="text-xs font-semibold text-rose-600">{keyError}</p>}
        <button
          type="submit"
          disabled={!keyInput.trim()}
          className="w-full py-2.5 rounded-xl btn-lexi-mint text-xs font-extrabold flex items-center justify-center gap-2 disabled:opacity-50"
        >
          <KeyRound className="w-4 h-4" />
          <span>Unlock Catalog Manager</span>
        </button>
      </form>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* Status strip: admin + response cache */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-white rounded-2xl p-4 border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2 text-xs font-bold text-emerald-700">
          <Unlock className="w-4 h-4" />
          <span>Admin access unlocked</span>
          <button onClick={handleLock} className="ml-2 text-slate-400 hover:text-slate-700 underline font-semibold">
            Lock
          </button>
        </div>

        <div className="flex items-center gap-3 flex-wrap text-xs">
          <span className="flex items-center gap-1.5 font-bold text-slate-600">
            <Zap className="w-4 h-4 text-amber-500" />
            Cache{cacheStats?.backend && cacheStats.backend !== 'off' ? ` (${cacheStats.backend === 'memory' ? 'server RAM' : 'Redis'})` : ''}:
            {cacheStats?.connected ? (
              <span className="text-emerald-700">active</span>
            ) : cacheStats?.configured ? (
              <span className="text-rose-600">unreachable</span>
            ) : (
              <span className="text-slate-400">off</span>
            )}
          </span>
          {cacheStats?.connected && (
            <span className="text-slate-500">
              {cacheStats.cached_keys} entries
              {cacheStats.memory_used_mb != null && ` · ${cacheStats.memory_used_mb}/${cacheStats.memory_limit_mb} MB`}
              {' · '}{cacheStats.hits} hits / {cacheStats.misses} misses
              {cacheStats.hit_ratio != null && ` (${Math.round(cacheStats.hit_ratio * 100)}%)`}
            </span>
          )}
          <button
            onClick={loadCacheStats}
            className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold flex items-center gap-1"
          >
            <RefreshCw className="w-3 h-3" /> Stats
          </button>
          {cacheStats?.connected && (
            <button
              onClick={handleFlush}
              className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-rose-50 hover:text-rose-700 text-slate-600 font-bold"
            >
              Flush cache
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Add phone form */}
        <form
          onSubmit={handleCreate}
          className="lg:col-span-2 bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4 self-start"
        >
          <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <Plus className="w-4 h-4 text-[#00D09C]" />
            Add phone manually
          </h3>

          <div className="grid grid-cols-2 gap-3">
            <label className="space-y-1">
              <span className="text-[11px] font-bold uppercase text-slate-400">Brand *</span>
              <input required value={form.brand} onChange={(e) => updateField('brand', e.target.value)} placeholder="Samsung" className={inputCls} />
            </label>
            <label className="space-y-1">
              <span className="text-[11px] font-bold uppercase text-slate-400">Model *</span>
              <input required value={form.model_name} onChange={(e) => updateField('model_name', e.target.value)} placeholder="Galaxy S25" className={inputCls} />
            </label>
            <label className="space-y-1">
              <span className="text-[11px] font-bold uppercase text-slate-400">Release date</span>
              <input type="date" value={form.release_date} onChange={(e) => updateField('release_date', e.target.value)} className={inputCls} />
            </label>
            <label className="space-y-1">
              <span className="text-[11px] font-bold uppercase text-slate-400">Market</span>
              <input value={form.country_market} onChange={(e) => updateField('country_market', e.target.value)} className={inputCls} />
            </label>
          </div>

          <label className="space-y-1 block">
            <span className="text-[11px] font-bold uppercase text-slate-400">Official URL</span>
            <input type="url" value={form.official_url} onChange={(e) => updateField('official_url', e.target.value)} placeholder="https://" className={inputCls} />
          </label>

          <label className="space-y-1 block">
            <span className="text-[11px] font-bold uppercase text-slate-400">Description</span>
            <textarea rows={2} value={form.description} onChange={(e) => updateField('description', e.target.value)} className={inputCls} />
          </label>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold uppercase text-slate-400">Variants</span>
              <button type="button" onClick={addVariant} className="text-xs font-bold text-emerald-700 hover:underline">
                + Add variant
              </button>
            </div>
            {form.variants.map((v, idx) => (
              <div key={idx} className="grid grid-cols-[1fr_1fr_1fr_auto] gap-2 items-center">
                <input value={v.ram} onChange={(e) => updateVariant(idx, 'ram', e.target.value)} placeholder="RAM (12GB)" className={inputCls} />
                <input value={v.storage} onChange={(e) => updateVariant(idx, 'storage', e.target.value)} placeholder="Storage" className={inputCls} />
                <input type="number" min="0" value={v.launch_price} onChange={(e) => updateVariant(idx, 'launch_price', e.target.value)} placeholder="₹ Price" className={inputCls} />
                <button type="button" onClick={() => removeVariant(idx)} className="p-2 text-slate-400 hover:text-rose-600" aria-label="Remove variant">
                  <X className="w-4 h-4" />
                </button>
                <input value={v.chipset} onChange={(e) => updateVariant(idx, 'chipset', e.target.value)} placeholder="Chipset (Snapdragon 8 Elite)" className={`${inputCls} col-span-3`} />
              </div>
            ))}
          </div>

          {formMsg && (
            <div
              className={`text-xs font-semibold p-3 rounded-xl border ${
                formMsg.type === 'ok' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200'
              }`}
            >
              {formMsg.text}
              {formMsg.id && (
                <Link to={`/products/${formMsg.id}`} className="ml-2 underline">View</Link>
              )}
            </div>
          )}

          <button
            type="submit"
            disabled={saving}
            className="w-full py-3 rounded-xl btn-lexi-mint text-xs font-extrabold flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Database className="w-4 h-4" />
            <span>{saving ? 'Saving…' : 'Add to catalog'}</span>
          </button>
        </form>

        {/* Existing entries */}
        <div className="lg:col-span-3 bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <Smartphone className="w-4 h-4 text-[#00D09C]" />
              Catalog entries <span className="text-slate-400 font-bold text-sm">({total})</span>
            </h3>
          </div>

          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search brand or model…"
              className={`${inputCls} pl-9`}
            />
          </div>

          <div className="divide-y divide-slate-100 max-h-[560px] overflow-y-auto -mx-2">
            {listLoading && products.length === 0 && (
              <p className="text-xs text-slate-400 p-4 text-center">Loading…</p>
            )}
            {!listLoading && products.length === 0 && (
              <p className="text-xs text-slate-400 p-4 text-center">No phones match.</p>
            )}
            {products.map((p) => (
              <div key={p.id} className="flex items-center justify-between gap-3 px-2 py-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-[10px] font-black uppercase tracking-wider text-emerald-700">{p.brand}</span>
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-md border ${SOURCE_STYLES[p.discovery_source] || SOURCE_STYLES.MANUAL}`}>
                      {p.discovery_source === 'AUTOMATED' ? 'AI discovered' : p.discovery_source.replace('_', ' ').toLowerCase()}
                    </span>
                  </div>
                  <Link to={`/products/${p.id}`} className="text-sm font-bold text-slate-900 hover:text-emerald-700 truncate block">
                    {p.model_name}
                  </Link>
                  <span className="text-[11px] text-slate-400">
                    {p.release_date || 'No release date'} · {p.variant_count} variant(s) · {p.total_owners_count} owner(s)
                  </span>
                </div>
                <button
                  onClick={() => handleDelete(p)}
                  disabled={deletingId === p.id}
                  className="px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-rose-50 border border-slate-200 hover:border-rose-200 text-slate-500 hover:text-rose-700 text-xs font-bold flex items-center gap-1.5 shrink-0 transition-colors disabled:opacity-50"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>{deletingId === p.id ? 'Deleting…' : 'Delete'}</span>
                </button>
              </div>
            ))}
          </div>

          {total > products.length && (
            <p className="text-[11px] text-slate-400 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5" />
              Showing the {products.length} most recent of {total}; search to narrow down.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

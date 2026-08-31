const RAW_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const API_BASE_URL = RAW_BASE_URL.replace(/\/+$/, '');

async function fetchJson(url, options = {}) {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorDetail = 'An unexpected error occurred';
    try {
      const errorJson = await response.json();
      if (Array.isArray(errorJson.detail)) {
        errorDetail = errorJson.detail
          .map(d => `${d.loc ? d.loc.filter(l => l !== 'body').join('.') : 'field'}: ${d.msg}`)
          .join(', ');
      } else if (typeof errorJson.detail === 'string') {
        errorDetail = errorJson.detail;
      } else if (errorJson.detail) {
        errorDetail = JSON.stringify(errorJson.detail);
      } else if (errorJson.message) {
        errorDetail = errorJson.message;
      }
    } catch {
      errorDetail = response.statusText || `Request failed with status ${response.status}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // Products
  getProducts: (params = {}) => {
    const query = new URLSearchParams();
    if (params.search) query.append('search', params.search);
    if (params.brand) query.append('brand', params.brand);
    if (params.status) query.append('status', params.status);
    if (params.sort_by) query.append('sort_by', params.sort_by);
    if (params.page) query.append('page', params.page);
    if (params.page_size) query.append('page_size', params.page_size);
    return fetchJson(`/products?${query.toString()}`);
  },

  getProduct: (id) => fetchJson(`/products/${id}`),

  createProduct: (productData) =>
    fetchJson('/products', {
      method: 'POST',
      body: JSON.stringify(productData),
    }),

  // Product Intelligence & Insights
  getProductInsights: (productId) => fetchJson(`/products/${productId}/insights`),

  getProductExperiences: (productId, params = {}) => {
    const query = new URLSearchParams();
    if (params.min_months) query.append('min_months', params.min_months);
    if (params.max_months) query.append('max_months', params.max_months);
    if (params.page) query.append('page', params.page);
    if (params.page_size) query.append('page_size', params.page_size);
    return fetchJson(`/products/${productId}/experiences?${query.toString()}`);
  },

  // Ownership & Reports
  registerOwnership: (ownershipData) =>
    fetchJson('/ownerships', {
      method: 'POST',
      body: JSON.stringify(ownershipData),
    }),

  getOwnership: (id) => fetchJson(`/ownerships/${id}`),

  addExperienceReport: (ownershipId, reportData) =>
    fetchJson(`/ownerships/${ownershipId}/reports`, {
      method: 'POST',
      body: JSON.stringify(reportData),
    }),

  // Comparison
  compareProducts: (productAId, productBId) =>
    fetchJson(`/products/compare?product_a=${productAId}&product_b=${productBId}`),

  // Suggestions
  submitSuggestion: (suggestionData) =>
    fetchJson('/product-suggestions', {
      method: 'POST',
      body: JSON.stringify(suggestionData),
    }),

  listSuggestions: (status) => {
    const query = status ? `?status=${status}` : '';
    return fetchJson(`/product-suggestions${query}`);
  },

  reviewSuggestion: (suggestionId, reviewData) =>
    fetchJson(`/product-suggestions/${suggestionId}/review`, {
      method: 'POST',
      body: JSON.stringify(reviewData),
    }),

  // Discovery
  triggerDiscovery: (payload = {}) =>
    fetchJson('/discovery/run', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  listDiscoveryRuns: (page = 1, pageSize = 20) =>
    fetchJson(`/discovery/runs?page=${page}&page_size=${pageSize}`),

  getDiscoveryRun: (id) => fetchJson(`/discovery/runs/${id}`),
};

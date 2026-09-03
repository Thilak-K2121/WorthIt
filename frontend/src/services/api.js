// ==============================================================================
// WorthIt Frontend - Centralized API Service Layer
// ==============================================================================
// This file acts as the primary HTTP client for communicating with the WorthIt
// backend REST API (deployed on Render / local development server).
// Handles URL normalization, query formatting, and defensive JSON error parsing.
// ==============================================================================

// Base URL configuration with fallback to the live Render production backend
const RAW_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://worthit-backend-v4ob.onrender.com/api/v1';
const API_BASE_URL = RAW_BASE_URL.replace(/\/+$/, '');

/**
 * Universal JSON Fetch Wrapper with Defensive Error Sanitization.
 * 
 * Why this function exists:
 * Formats outgoing headers and intercepts HTTP error responses (e.g. 422, 500).
 * Unpacks FastAPI validation error arrays into human-readable strings so the UI
 * never renders raw "[object Object]" error alerts.
 * 
 * @param {string} url - API endpoint relative path.
 * @param {object} options - Fetch options (method, headers, body).
 * @returns {Promise<any>} Parsed JSON response.
 */
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
      // Handle FastAPI Pydantic 422 error list: [{ loc: ['body', 'field'], msg: 'error' }]
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
  // ----------------------------------------------------------------------------
  // Smartphone Products & Catalog Endpoints
  // ----------------------------------------------------------------------------

  /**
   * Fetches paginated smartphone catalog list with search and brand filters.
   * @param {object} params - { search, brand, status, sort_by, page, page_size }
   */
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

  /**
   * Fetches distinct list of all active brand names in catalog.
   */
  getBrands: () => fetchJson('/products/brands'),

  /**
   * Retrieves single smartphone specifications and hardware variants.
   * @param {string} id - Product UUID.
   */
  getProduct: (id) => fetchJson(`/products/${id}`),

  /**
   * Manually creates a new smartphone product.
   * @param {object} productData - { brand, model_name, release_date, variants }
   */
  createProduct: (productData) =>
    fetchJson('/products', {
      method: 'POST',
      body: JSON.stringify(productData),
    }),

  // ----------------------------------------------------------------------------
  // Longitudinal Intelligence & Experience Reports
  // ----------------------------------------------------------------------------

  /**
   * Computes longitudinal scores, battery degradation, and sample confidence.
   * @param {string} productId - Product UUID.
   */
  getProductInsights: (productId) => fetchJson(`/products/${productId}/insights`),

  /**
   * Retrieves historical user experience reports for a specific device.
   * @param {string} productId - Product UUID.
   */
  getProductExperiences: (productId, params = {}) => {
    const query = new URLSearchParams();
    if (params.min_months) query.append('min_months', params.min_months);
    if (params.max_months) query.append('max_months', params.max_months);
    if (params.page) query.append('page', params.page);
    if (params.page_size) query.append('page_size', params.page_size);
    return fetchJson(`/products/${productId}/experiences?${query.toString()}`);
  },

  // ----------------------------------------------------------------------------
  // Ownership Intake & Experience Submission
  // ----------------------------------------------------------------------------

  /**
   * Registers a new device ownership record and nested initial review.
   * @param {object} ownershipData - { product_id, purchase_price, initial_report }
   */
  registerOwnership: (ownershipData) =>
    fetchJson('/ownerships', {
      method: 'POST',
      body: JSON.stringify(ownershipData),
    }),

  /**
   * Fetches an ownership record by UUID.
   */
  getOwnership: (id) => fetchJson(`/ownerships/${id}`),

  /**
   * Appends a follow-up longitudinal review (e.g. 6m, 12m, 24m update) to an existing ownership.
   */
  addExperienceReport: (ownershipId, reportData) =>
    fetchJson(`/ownerships/${ownershipId}/reports`, {
      method: 'POST',
      body: JSON.stringify(reportData),
    }),

  // ----------------------------------------------------------------------------
  // Side-by-Side Smartphone Comparison
  // ----------------------------------------------------------------------------

  /**
   * Compares 2 smartphones side-by-side across longitudinal metrics.
   * @param {string} productAId - First product UUID.
   * @param {string} productBId - Second product UUID.
   */
  compareProducts: (productAId, productBId) =>
    fetchJson(`/products/compare?product_a=${productAId}&product_b=${productBId}`),

  // ----------------------------------------------------------------------------
  // Community Suggestions & Missing Device Requests
  // ----------------------------------------------------------------------------

  /**
   * Submits a user request to add a missing smartphone model.
   */
  submitSuggestion: (suggestionData) =>
    fetchJson('/product-suggestions', {
      method: 'POST',
      body: JSON.stringify(suggestionData),
    }),

  /**
   * Lists submitted community suggestions (filtered by 'PENDING', 'APPROVED', etc.).
   */
  listSuggestions: (status) => {
    const query = status ? `?status=${status}` : '';
    return fetchJson(`/product-suggestions${query}`);
  },

  /**
   * Approves or rejects a community suggestion.
   */
  reviewSuggestion: (suggestionId, reviewData) =>
    fetchJson(`/product-suggestions/${suggestionId}/review`, {
      method: 'POST',
      body: JSON.stringify(reviewData),
    }),

  // ----------------------------------------------------------------------------
  // Automated AI Web Discovery Endpoints
  // ----------------------------------------------------------------------------

  /**
   * Triggers an automated AI web discovery job (Tavily Search + Gemini Extraction).
   * @param {object} payload - { query_topic, max_results }
   */
  triggerDiscovery: (payload = {}) =>
    fetchJson('/discovery/run', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  /**
   * Lists past automated AI discovery runs with status and provenance logs.
   */
  listDiscoveryRuns: (page = 1, pageSize = 20) =>
    fetchJson(`/discovery/runs?page=${page}&page_size=${pageSize}`),

  /**
   * Fetches full audit details for a specific discovery run.
   */
  getDiscoveryRun: (id) => fetchJson(`/discovery/runs/${id}`),
};

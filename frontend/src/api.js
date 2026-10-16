// The browser only ever talks to /api on its own origin. Nginx (Compose) or the
// Kubernetes Ingress routes it to the FastAPI backend.
async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* non-JSON error body */
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  list: (params = {}) => {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== '' && v !== false));
    return request(`/products${qs.toString() ? `?${qs}` : ''}`);
  },
  stats: () => request('/products/stats'),
  create: (data) => request('/products', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => request(`/products/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  adjust: (id, delta) => request(`/products/${id}/adjust`, { method: 'POST', body: JSON.stringify({ delta }) }),
  remove: (id) => request(`/products/${id}`, { method: 'DELETE' }),
};

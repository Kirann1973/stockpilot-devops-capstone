import { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from './api.js';
import ProductModal from './ProductModal.jsx';

const inr = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 });

const STATUS_LABEL = { IN_STOCK: 'In stock', LOW_STOCK: 'Low stock', OUT_OF_STOCK: 'Out of stock' };

export default function App() {
  const [products, setProducts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [lowOnly, setLowOnly] = useState(false);
  const [editing, setEditing] = useState(null); // null = closed, {} = new, product = edit
  const [activity, setActivity] = useState([]);
  const [navOpen, setNavOpen] = useState(false);

  const log = (text) => setActivity((a) => [{ text, at: new Date() }, ...a].slice(0, 8));

  const load = useCallback(async () => {
    try {
      const [list, s] = await Promise.all([api.list({ q: query, category, low_stock: lowOnly }), api.stats()]);
      setProducts(list);
      setStats(s);
      setError('');
    } catch (e) {
      setError(`Cannot reach the StockPilot API (${e.message}). Is the backend running?`);
    } finally {
      setLoading(false);
    }
  }, [query, category, lowOnly]);

  useEffect(() => {
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
  }, [load]);

  const categories = useMemo(() => [...new Set(products.map((p) => p.category))].sort(), [products]);

  async function run(action, message) {
    try {
      await action();
      log(message);
      await load();
    } catch (e) {
      alert(e.message);
    }
  }

  async function save(form) {
    if (editing?.id) {
      const { sku, ...rest } = form;
      await run(() => api.update(editing.id, rest), `Updated ${form.name}`);
    } else {
      await run(() => api.create(form), `Added ${form.name} (${form.sku})`);
    }
    setEditing(null);
  }

  return (
    <div className="layout">
      <aside className={`sidebar ${navOpen ? 'open' : ''}`}>
        <div className="brand">
          <span className="logo">📦</span>
          <div>
            <strong>StockPilot</strong>
            <small>Inventory control</small>
          </div>
        </div>
        <nav>
          <a className="active">Dashboard</a>
          <a onClick={() => setLowOnly(true)}>Reorder list</a>
          <a href="/docs" target="_blank" rel="noreferrer">API docs</a>
        </nav>
        <div className="pipeline">
          <small>Delivery pipeline</small>
          <ol>
            {['Test', 'Build', 'Scan', 'Push', 'Deploy'].map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ol>
        </div>
        <footer>Built by Kiran · Roll No. 10446</footer>
      </aside>

      <main>
        <header className="topbar">
          <button className="menu" aria-label="Toggle menu" onClick={() => setNavOpen((o) => !o)}>☰</button>
          <div>
            <h1>Inventory dashboard</h1>
            <p className="muted">Track stock levels, spot shortages and restock on time.</p>
          </div>
          <button className="primary" onClick={() => setEditing({})}>+ Add product</button>
        </header>

        {error && <div className="banner error">{error}</div>}

        <section className="kpis">
          <Kpi label="Products" value={stats?.total_products ?? '–'} />
          <Kpi label="Units in stock" value={stats?.total_units?.toLocaleString('en-IN') ?? '–'} />
          <Kpi label="Inventory value" value={stats ? inr.format(stats.inventory_value) : '–'} />
          <Kpi label="Low stock" value={stats?.low_stock ?? '–'} tone="warn" />
          <Kpi label="Out of stock" value={stats?.out_of_stock ?? '–'} tone="danger" />
        </section>

        <div className="content">
          <section className="card table-card">
            <div className="filters">
              <input
                type="search"
                placeholder="Search name, SKU or supplier…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <select value={category} onChange={(e) => setCategory(e.target.value)}>
                <option value="">All categories</option>
                {categories.map((c) => (
                  <option key={c}>{c}</option>
                ))}
              </select>
              <label className="toggle">
                <input type="checkbox" checked={lowOnly} onChange={(e) => setLowOnly(e.target.checked)} />
                Needs reorder
              </label>
            </div>

            {loading ? (
              <p className="muted pad">Loading inventory…</p>
            ) : products.length === 0 ? (
              <p className="muted pad">No products match. Add one with “+ Add product”.</p>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>Category</th>
                      <th className="num">Qty</th>
                      <th className="num">Unit price</th>
                      <th>Status</th>
                      <th aria-label="Actions" />
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((p) => (
                      <tr key={p.id}>
                        <td data-label="Product">
                          <strong>{p.name}</strong>
                          <small className="muted">{p.sku} · {p.supplier}</small>
                        </td>
                        <td data-label="Category">{p.category}</td>
                        <td data-label="Qty" className="num">
                          <div className="stepper">
                            <button onClick={() => run(() => api.adjust(p.id, -1), `Shipped 1 × ${p.name}`)} disabled={p.quantity === 0}>−</button>
                            <span>{p.quantity}</span>
                            <button onClick={() => run(() => api.adjust(p.id, 10), `Received 10 × ${p.name}`)}>+10</button>
                          </div>
                        </td>
                        <td data-label="Unit price" className="num">{inr.format(p.unit_price)}</td>
                        <td data-label="Status">
                          <span className={`badge ${p.stock_status.toLowerCase()}`}>{STATUS_LABEL[p.stock_status]}</span>
                        </td>
                        <td className="actions">
                          <button className="ghost" onClick={() => setEditing(p)}>Edit</button>
                          <button
                            className="ghost danger"
                            onClick={() => confirm(`Delete ${p.name}?`) && run(() => api.remove(p.id), `Deleted ${p.name}`)}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <aside className="card activity">
            <h2>Recent activity</h2>
            {activity.length === 0 ? (
              <p className="muted">Changes you make appear here.</p>
            ) : (
              <ul>
                {activity.map((a, i) => (
                  <li key={i}>
                    {a.text}
                    <small className="muted">{a.at.toLocaleTimeString()}</small>
                  </li>
                ))}
              </ul>
            )}
          </aside>
        </div>
      </main>

      {editing && <ProductModal product={editing} onClose={() => setEditing(null)} onSave={save} />}
    </div>
  );
}

function Kpi({ label, value, tone }) {
  return (
    <div className={`card kpi ${tone ?? ''}`}>
      <small>{label}</small>
      <strong>{value}</strong>
    </div>
  );
}

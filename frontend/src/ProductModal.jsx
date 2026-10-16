import { useState } from 'react';

const EMPTY = {
  name: '',
  sku: '',
  category: 'General',
  supplier: '',
  quantity: 0,
  reorder_level: 10,
  unit_price: 0,
  description: '',
};

export default function ProductModal({ product, onClose, onSave }) {
  const isEdit = Boolean(product.id);
  const [form, setForm] = useState({ ...EMPTY, ...product });
  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.type === 'number' ? Number(e.target.value) : e.target.value }));

  function submit(e) {
    e.preventDefault();
    const { id, created_at, updated_at, stock_status, ...payload } = form;
    onSave({ ...payload, supplier: payload.supplier || 'Unknown' });
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <form className="modal card" onClick={(e) => e.stopPropagation()} onSubmit={submit}>
        <h2>{isEdit ? 'Edit product' : 'Add product'}</h2>
        <div className="grid">
          <label>Name<input required value={form.name} onChange={set('name')} /></label>
          <label>SKU<input required value={form.sku} onChange={set('sku')} disabled={isEdit} /></label>
          <label>Category<input value={form.category} onChange={set('category')} /></label>
          <label>Supplier<input value={form.supplier} onChange={set('supplier')} /></label>
          <label>Quantity<input type="number" min="0" value={form.quantity} onChange={set('quantity')} /></label>
          <label>Reorder level<input type="number" min="0" value={form.reorder_level} onChange={set('reorder_level')} /></label>
          <label>Unit price (₹)<input type="number" min="0" step="0.01" value={form.unit_price} onChange={set('unit_price')} /></label>
        </div>
        <label>Description<textarea rows="2" value={form.description} onChange={set('description')} /></label>
        <div className="modal-actions">
          <button type="button" className="ghost" onClick={onClose}>Cancel</button>
          <button type="submit" className="primary">{isEdit ? 'Save changes' : 'Add product'}</button>
        </div>
      </form>
    </div>
  );
}

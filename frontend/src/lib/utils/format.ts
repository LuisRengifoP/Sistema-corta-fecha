/** Formatea una fecha ISO (YYYY-MM-DD o datetime) a DD/MM/AAAA. */
export function fechaLocal(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '—';
  const dd = String(d.getDate()).padStart(2, '0');
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  return `${dd}/${mm}/${yyyy}`;
}

/** Formatea fecha + hora a DD/MM/AAAA HH:mm. */
export function fechaHora(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '—';
  const hh = String(d.getHours()).padStart(2, '0');
  const min = String(d.getMinutes()).padStart(2, '0');
  return `${fechaLocal(iso)} ${hh}:${min}`;
}

/** Numero compacto (quita decimales .000). */
export function num(valor: string | number): string {
  const n = typeof valor === 'string' ? Number(valor) : valor;
  if (Number.isNaN(n)) return String(valor);
  return Number.isInteger(n) ? String(n) : n.toFixed(2).replace(/\.?0+$/, '');
}

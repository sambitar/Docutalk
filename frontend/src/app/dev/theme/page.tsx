const SWATCHES: { name: string; varName: string; hex: string }[] = [
  { name: "Background", varName: "--color-bg", hex: "#FAFBFF" },
  { name: "BG muted", varName: "--color-bg-muted", hex: "#F3F4F8" },
  { name: "Surface", varName: "--color-surface", hex: "#FFFFFF" },
  { name: "Brand", varName: "--color-brand", hex: "#6D28D9" },
  { name: "Brand hover", varName: "--color-brand-hover", hex: "#5B21B6" },
  { name: "Brand muted", varName: "--color-brand-muted", hex: "#8B5CF6" },
  { name: "Brand subtle", varName: "--color-brand-subtle", hex: "#EDE9FE" },
  { name: "Metal border", varName: "--color-border-metal", hex: "#C5C8D0" },
  { name: "Text", varName: "--color-text", hex: "#0F172A" },
  { name: "Text secondary", varName: "--color-text-secondary", hex: "#64748B" },
];

export default function ThemeDevPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <p className="text-sm font-medium text-brand">Docutalk / design</p>
      <h1 className="mt-2 text-3xl font-semibold tracking-tight text-ink">
        Theme tokens
      </h1>
      <p className="mt-2 text-ink-secondary">
        Purple + white metallic — brand purple for actions only.
      </p>

      <section className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-3">
        {SWATCHES.map((s) => (
          <div key={s.varName} className="surface-metal p-3">
            <div
              className="mb-3 h-16 rounded-md border border-metal-subtle"
              style={{ background: `var(${s.varName})` }}
            />
            <p className="text-sm font-medium text-ink">{s.name}</p>
            <p className="text-xs text-ink-muted">{s.hex}</p>
            <p className="text-xs text-ink-secondary">{s.varName}</p>
          </div>
        ))}
      </section>

      <section className="surface-metal mt-10 space-y-4 p-6">
        <h2 className="text-lg font-semibold text-ink">Components</h2>
        <div className="flex flex-wrap gap-3">
          <button type="button" className="btn-brand">
            Primary action
          </button>
          <button type="button" className="btn-metal">
            Secondary
          </button>
        </div>
        <input
          className="input-metal max-w-md"
          placeholder="Metallic input"
          defaultValue=""
        />
        <div
          className="h-20 rounded-lg border border-metal-border"
          style={{ background: "var(--gradient-metal)" }}
        />
      </section>
    </main>
  );
}

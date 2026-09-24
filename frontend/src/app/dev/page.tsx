// Route /dev — owner: P6 (renderer). Keep this file thin: render a component from the owning module.
export default function Page() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-3 px-4 py-16">
      <p className="text-sm text-muted">/dev · P6 (renderer)</p>
      <h1 className="font-display text-3xl font-bold text-deep-navy">Renderer playground</h1>
      <p className="text-muted">แสดง mock ของทุก response_type โดยไม่ต้องมี backend</p>
    </main>
  );
}

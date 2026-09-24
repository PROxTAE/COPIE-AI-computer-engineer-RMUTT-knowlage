// Route /chat — owner: P1 (core). Keep this file thin: render a component from the owning module.
export default function Page() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-3 px-4 py-16">
      <p className="text-sm text-muted">/chat · P1 (core)</p>
      <h1 className="font-display text-3xl font-bold text-deep-navy">Main AI Experience</h1>
      <p className="text-muted">COPIE 3D + Renderer + History + Suggestions จะประกอบกันที่นี่</p>
    </main>
  );
}

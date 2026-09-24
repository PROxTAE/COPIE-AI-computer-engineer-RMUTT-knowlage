// Route /onboarding — owner: P2 (user). Keep this file thin: render a component from the owning module.
export default function Page() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-3 px-4 py-16">
      <p className="text-sm text-muted">/onboarding · P2 (user)</p>
      <h1 className="font-display text-3xl font-bold text-deep-navy">Onboarding</h1>
      <p className="text-muted">ชื่อ ช่วงอายุ สถานะผู้ใช้ และชั้นปี</p>
    </main>
  );
}

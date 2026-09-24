// Route /login — owner: P2 (user). Keep this file thin: render a component from the owning module.
export default function Page() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-3 px-4 py-16">
      <p className="text-sm text-muted">/login · P2 (user)</p>
      <h1 className="font-display text-3xl font-bold text-deep-navy">เข้าสู่ระบบ</h1>
      <p className="text-muted">Continue with Google และ Dev Login</p>
    </main>
  );
}

import Link from "next/link";

// Route / — owner: P1. Will redirect by user state (login → onboarding → chat).
const routes = [
  { href: "/login", label: "Login", owner: "P2" },
  { href: "/onboarding", label: "Onboarding", owner: "P2" },
  { href: "/chat", label: "Chat", owner: "P1" },
  { href: "/dev", label: "Renderer playground", owner: "P6" },
];

export default function Home() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-6 px-4 py-16">
      <h1 className="font-display text-4xl font-bold text-deep-navy">COPIE</h1>
      <p className="text-muted">AI Assistant ภาควิชาวิศวกรรมคอมพิวเตอร์ RMUTT</p>
      <nav className="flex flex-wrap gap-3">
        {routes.map((r) => (
          <Link
            key={r.href}
            href={r.href}
            className="rounded-md border border-copie-teal/40 bg-surface px-4 py-2 text-sm hover:bg-copie-teal/10"
          >
            {r.label} <span className="text-muted">· {r.owner}</span>
          </Link>
        ))}
      </nav>
    </main>
  );
}

import { redirect } from "next/navigation";

import { ThemePreview } from "@/modules/core";

export default function Page() {
  if (process.env.NODE_ENV === "development") return <ThemePreview />;
  redirect("/login");
}

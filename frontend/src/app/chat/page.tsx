import { AuthenticatedChatPage } from "@/modules/user";

export default async function Page({ searchParams }: { searchParams: Promise<{ debug?: string }> }) {
  const { debug } = await searchParams;
  return <AuthenticatedChatPage debug={process.env.NODE_ENV === "development" && debug === "1"} />;
}

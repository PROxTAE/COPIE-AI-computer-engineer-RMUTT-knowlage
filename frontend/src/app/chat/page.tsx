import { ChatPage } from "@/modules/core";

export default async function Page({ searchParams }: { searchParams: Promise<{ debug?: string }> }) {
  const { debug } = await searchParams;
  return <ChatPage debug={process.env.NODE_ENV === "development" && debug === "1"} />;
}

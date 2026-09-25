import type { Metadata } from "next";
import { Chakra_Petch, IBM_Plex_Sans_Thai, Kanit, Unbounded } from "next/font/google";
import "./globals.css";

// White Cyberism type system (00_SHARED_PROJECT_CONTEXT.md §3)
const heading = Kanit({
  variable: "--ff-heading",
  subsets: ["thai", "latin"],
  weight: ["500", "600", "700", "800"],
  style: ["normal", "italic"],
});

const body = IBM_Plex_Sans_Thai({
  variable: "--ff-body",
  subsets: ["thai", "latin"],
  weight: ["400", "500", "600"],
});

const label = Chakra_Petch({
  variable: "--ff-label",
  subsets: ["thai", "latin"],
  weight: ["500", "600", "700"],
});

const wordmark = Unbounded({
  variable: "--ff-wordmark",
  subsets: ["latin"],
  weight: ["800", "900"],
});

export const metadata: Metadata = {
  title: "COPIE · CE RMUTT",
  description: "AI Assistant ภาควิชาวิศวกรรมคอมพิวเตอร์ มหาวิทยาลัยเทคโนโลยีราชมงคลธัญบุรี",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="th"
      data-theme="light"
      className={`light ${heading.variable} ${body.variable} ${label.variable} ${wordmark.variable} h-full antialiased`}
    >
      <body className="min-h-full font-sans">{children}</body>
    </html>
  );
}

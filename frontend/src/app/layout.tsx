import type { Metadata, Viewport } from "next";
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

// viewport-fit=cover lets env(safe-area-inset-*) report the real notch / status bar sizes.
export const viewport: Viewport = { width: "device-width", initialScale: 1, viewportFit: "cover" };

// In-app browsers (Discord, LINE, Instagram, Facebook ...) draw their own bar over the top of the
// page without reporting a safe area, which hid the header. Flag them so CSS can leave a gap.
// iOS in-app webviews have no "Safari/" token; Android ones add "wv" or the app's name.
const IN_APP_SCRIPT = `(function(){var u=navigator.userAgent;var ios=/iPhone|iPad|iPod/.test(u)&&!/Safari\//.test(u)&&!/CriOS|FxiOS|EdgiOS/.test(u);var app=/FBAN|FBAV|Instagram|Line\/|Discord|; wv\)|MicroMessenger|TikTok|Snapchat|Twitter/i.test(u);if(ios||app)document.documentElement.setAttribute('data-inapp','1');})();`;

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="th"
      data-theme="light"
      className={`light ${heading.variable} ${body.variable} ${label.variable} ${wordmark.variable} h-full antialiased`}
    >
      <body className="min-h-full font-sans">
        <script dangerouslySetInnerHTML={{ __html: IN_APP_SCRIPT }} />
        {children}
      </body>
    </html>
  );
}

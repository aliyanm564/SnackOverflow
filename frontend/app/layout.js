import "./globals.css";
import Nav from "@/components/ui/Nav";

export const metadata = {
  title: "SnackOverflow",
  description: "SnackOverflow frontend",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Nav />
        {children}
      </body>
    </html>
  );
}

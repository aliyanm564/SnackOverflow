import "./globals.css";

export const metadata = {
  title: "SnackOverflow",
  description: "SnackOverflow frontend",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

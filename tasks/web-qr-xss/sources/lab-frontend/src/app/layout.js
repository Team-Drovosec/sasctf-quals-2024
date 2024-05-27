import { Inter, Poppins } from "next/font/google";
import "./globals.css";



const poppins = Poppins({subsets: ['latin'], weight: '400'})
export const metadata = {
  title: "LiquidLab",
  description: "Welcome to the PCRMobile™ by LiquidLab.",
};

export default function RootLayout({ children }) {
  return (
    <html>
      <body className={poppins.className}>{children}</body>
    </html>
  );
}

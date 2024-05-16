"use client";
import "jsvectormap/dist/css/jsvectormap.css";
import "flatpickr/dist/flatpickr.min.css";
import "@/css/satoshi.css";
import "@/css/style.css";
import React, { useEffect, useState } from "react";
import Loader from "@/components/common/Loader";
import { ToastContainer } from "react-toastify";
import { toastOptions } from '@/app/toastConfig';
import { AuthActions } from "@/app/auth/utils";
import { toast } from "react-toastify";
import { useRouter, usePathname } from "next/navigation";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [loading, setLoading] = useState<boolean>(true);
  const { getToken, loggedIn } = AuthActions();
  const router = useRouter();
  const pathname = usePathname();

  const allowedPaths = ["/auth/signin", "/auth/signup"];

  useEffect(() => {
    setLoading(true);
    const handleRedirect = () => {
      if (!loggedIn() && !allowedPaths.includes(pathname)) {
        toast.warn("Please sign in");
        router.push("/auth/signin");
      } else if (loggedIn() && allowedPaths.includes(pathname)) {
        toast.warn("You're already signed in!");
        router.push("/");
      }
      setLoading(false);
    };
    handleRedirect();
  }, [pathname, loggedIn]);

  return (
    <html lang="en">
      <body suppressHydrationWarning={true}>
        <div className="dark:bg-boxdark-2 dark:text-bodydark">
          {loading ? <Loader visible={loading} /> : children}
        </div>
        <ToastContainer {...toastOptions} />
      </body>
    </html>
  );
}

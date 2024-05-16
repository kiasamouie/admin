"use client";

import React, { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCaretDown, faCaretRight } from '@fortawesome/free-solid-svg-icons';

import { sidebarMenu, SidebarMenuItem } from './sidebarMenu';

interface SidebarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (arg: boolean) => void;
}

const Sidebar = ({ sidebarOpen, setSidebarOpen }: SidebarProps) => {
  const pathname = usePathname();

  const trigger = useRef<HTMLButtonElement | null>(null);
  const sidebar = useRef<HTMLDivElement | null>(null);

  let storedSidebarExpanded = "true";

  const [sidebarExpanded, setSidebarExpanded] = useState(
    storedSidebarExpanded === null ? false : storedSidebarExpanded === "true"
  );

  const [collapsedItems, setCollapsedItems] = useState<Record<number, boolean>>({});
  const [hoveredParentIndex, setHoveredParentIndex] = useState<number | null>(null);

  // Close on click outside
  useEffect(() => {
    const clickHandler = ({ target }: MouseEvent) => {
      if (!sidebar.current || !trigger.current) return;
      if (
        !sidebarOpen ||
        sidebar.current.contains(target as Node) ||
        trigger.current.contains(target as Node)
      )
        return;
      setSidebarOpen(false);
    };
    document.addEventListener("click", clickHandler);
    return () => document.removeEventListener("click", clickHandler);
  });

  // Close if the esc key is pressed
  useEffect(() => {
    const keyHandler = ({ key }: KeyboardEvent) => {
      if (!sidebarOpen || key !== "Escape") return;
      setSidebarOpen(false);
    };
    document.addEventListener("keydown", keyHandler);
    return () => document.removeEventListener("keydown", keyHandler);
  });

  useEffect(() => {
    localStorage.setItem("sidebar-expanded", sidebarExpanded.toString());
    if (sidebarExpanded) {
      document.querySelector("body")?.classList.add("sidebar-expanded");
    } else {
      document.querySelector("body")?.classList.remove("sidebar-expanded");
    }
  }, [sidebarExpanded]);

  // Toggle function to collapse/expand menu item
  const toggleCollapse = (index: number) => {
    setCollapsedItems((prevState) => ({
      ...prevState,
      [index]: !prevState[index],
    }));
  };

  // Ensure the parent menu of the active child item is open
  useEffect(() => {
    sidebarMenu.forEach((item, index) => {
      if (item.children) {
        const isChildActive = item.children.some((child) => pathname.includes(child.url));
        if (isChildActive) {
          setCollapsedItems((prevState) => ({
            ...prevState,
            [index]: true,
          }));
        }
      }
    });
  }, [pathname]);

  const isActiveItem = (url: string, children?: SidebarMenuItem[]): boolean => {
    if (pathname === url) {
      return true;
    }
    if (children) {
      return children.some((child) => pathname.includes(child.url));
    }
    return false;
  };

  return (
    <aside
      ref={sidebar}
      className={`absolute left-0 top-0 z-9999 flex h-screen w-72.5 flex-col overflow-y-hidden bg-black duration-300 ease-linear dark:bg-boxdark lg:static lg:translate-x-0 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
    >
      {/* <!-- SIDEBAR HEADER --> */}
      <div className="flex items-center justify-between gap-2 px-6 py-5.5 lg:py-6.5">
        {/* <Link href="/">
          <Image
            width={176}
            height={32}
            src={"/images/logo/logo.svg"}
            alt="Logo"
            priority
          />
        </Link>

        <button
          ref={trigger}
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-controls="sidebar"
          aria-expanded={sidebarOpen}
          className="block lg:hidden"
        >
          <FontAwesomeIcon icon={faMobileButton} />
        </button> */}
      </div>
      {/* <!-- SIDEBAR HEADER --> */}

      <div className="no-scrollbar flex flex-col overflow-y-auto duration-300 ease-linear">
        {/* <!-- Sidebar Menu --> */}
        <nav className="lg:px-6">
          {/* <!-- Menu Group --> */}
          <ul className="mb-6 flex flex-col gap-1.5">
            {sidebarMenu.map((item, index) => {
              const isActive = isActiveItem(item.url, item.children);
              const isParentHovered = index === hoveredParentIndex;
              return (
                <li key={index} className="relative">
                  <div className="flex items-center justify-between">
                    <Link
                      href={item.url}
                      className={`group relative flex items-center gap-2.5 px-4 py-2 font-medium text-bodydark1 duration-300 ease-in-out w-full ${isActive || isParentHovered ? "bg-graydark dark:bg-meta-4 rounded-full" : "hover:bg-graydark dark:hover:bg-meta-4 rounded-full"}`}
                    >
                      {item.icon && <FontAwesomeIcon icon={item.icon} className="text-blue-500" />}
                      {item.title}
                    </Link>
                    {item.children && (
                      <button
                        onClick={() => toggleCollapse(index)}
                        className="px-2 focus:outline-none"
                      >
                        <FontAwesomeIcon
                          icon={collapsedItems[index] ? faCaretDown : faCaretRight}
                          className="text-gray-500"
                        />
                      </button>
                    )}
                  </div>
                  {item.children && collapsedItems[index] && (
                    <ul className="ml-4 mt-2 flex flex-col gap-1.5 pl-4">
                      {item.children.map((subItem, subIndex) => {
                        const isSubActive = pathname.includes(subItem.url);
                        return (
                          <li
                            key={subIndex}
                            onMouseEnter={() => setHoveredParentIndex(index)}
                            onMouseLeave={() => setHoveredParentIndex(null)}
                          >
                            <Link
                              href={subItem.url}
                              className={`group relative flex items-center gap-2.5 px-4 py-2 font-medium text-bodydark1 duration-300 ease-in-out ${isSubActive ? "bg-graydark dark:bg-meta-4 rounded-full" : "rounded-sm hover:rounded-full hover:bg-graydark dark:hover:bg-meta-4"}`}
                            >
                              <FontAwesomeIcon icon={subItem.icon} className="text-blue-300" />
                              {subItem.title}
                            </Link>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </li>
              );
            })}
          </ul>
        </nav>
        {/* <!-- Sidebar Menu --> */}
      </div>
    </aside>
  );
};

export default Sidebar;

import { faDashboard, faDownload, faUser, faWrench } from '@fortawesome/free-solid-svg-icons';

export interface SidebarMenuItem {
  title: string;
  icon?: any;
  url: string;
  children?: SidebarMenuItem[];
}

export const sidebarMenu: SidebarMenuItem[] = [
  {
    title: "Dashboard",
    icon: faDashboard,
    url: "/"
  },
  {
    title: "Download",
    icon: faDownload,
    url: "/download",
  },
  {
    title: "Settings",
    icon: faWrench,
    url: "/settings",
    children: [
      {
        title: "Profile",
        url: "/settings/profile",
        icon: faUser
      }
    ]
  }
];

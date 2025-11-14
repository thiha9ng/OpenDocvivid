"use client"

import * as React from "react"
import { usePathname } from "next/navigation"
import { useSession } from "next-auth/react"
import {
  House,
  Book,
  Sparkles,
  LoaderPinwheel,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavInfo } from "@/components/nav-info"
import { NavUser } from "@/components/nav-user"
import { NavLogo } from "@/components/nav-logo"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar"

// Navigation data
const navData = {
  navMain: [
    {
      title: "Home",
      url: "/",
      icon: House,
    },
    {
      title: "Library",
      url: "/library",
      icon: Book,
    },
    {
      title: "Explore",
      url: "/explore",
      icon: LoaderPinwheel,
    },
  ],
  infos: [
    {
      name: "Upgrade to Pro",
      url: "/pricing",
      icon: Sparkles,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const pathname = usePathname()
  const { data: session } = useSession()
  
  // Dynamically set isActive based on current pathname
  const navMainWithActive = navData.navMain.map(item => ({
    ...item,
    isActive: pathname === item.url
  }))

  const infosWithActive = navData.infos.map(item => ({
    ...item,
    isActive: pathname === item.url
  }))

  // Create user object from session data if available
  const user = session?.user ? {
    name: session.user.name || '',
    email: session.user.email || '',
    avatar: session.user.image || ''
  } : null

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <NavLogo />
      </SidebarHeader>
      <SidebarContent className="justify-between">
        <NavMain items={navMainWithActive} />
        <NavInfo infos={infosWithActive} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}

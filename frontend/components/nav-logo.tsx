"use client"

import * as React from "react"
import Image from "next/image"

import {
  SidebarMenu,
  SidebarMenuItem,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar"

export function NavLogo() {
  const { state } = useSidebar()
  const isCollapsed = state === "collapsed"

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        {isCollapsed ? (
          <div className="flex items-center justify-center p-2">
            <SidebarTrigger />
          </div>
        ) : (
          <div className="flex items-center gap-2 px-2 py-1.5">
            <Image 
              src="/logo.svg" 
              alt="DocVivid Logo" 
              width={32} 
              height={32} 
              className="size-8 rounded-sm"
            />
            <span className="text-lg font-semibold">DocVivid</span>
            <SidebarTrigger className="ml-auto" />
          </div>
        )}
      </SidebarMenuItem>
    </SidebarMenu>
  )
}

"use client"

import {
  Mail,
  type LucideIcon,
} from "lucide-react"
import Link from "next/link"
import { 
  FaDiscord,
} from "react-icons/fa";
import { 
  BsTwitterX
} from "react-icons/bs";
import {
  SidebarGroup,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarSeparator,
} from "@/components/ui/sidebar"

export function NavInfo({
  infos,
}: {
  infos: {
    name: string
    url: string
    icon: LucideIcon
    isActive?: boolean
  }[]
}) {
  return (
    <SidebarGroup>
      <SidebarMenu>
        {infos.map((item) => (
          <SidebarMenuItem key={item.name}>
            <SidebarMenuButton 
              tooltip={item.name} 
              asChild
              isActive={item.isActive}
              className="cursor-pointer transition-all duration-200 hover:scale-[1.02]"
            >
              <Link href={item.url}>
                <item.icon className={item.isActive ? "text-primary" : ""} />
                <span className={item.isActive ? "font-semibold" : ""}>{item.name}</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ))}
        <SidebarMenuItem className="group-data-[collapsible=icon]:hidden">
          <SidebarSeparator />
          <div className="flex items-center gap-3 px-2 py-2">
            <a 
              href="https://x.com/tensor_chovy" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-sidebar-foreground/70 hover:text-sidebar-foreground transition-colors"
            >
              <BsTwitterX className="size-4" />
            </a>
            <a 
              href="https://discord.gg/AJcneUPp" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-sidebar-foreground/70 hover:text-sidebar-foreground transition-colors"
            >
              <FaDiscord className="size-4" />
            </a>
            <a 
              href="mailto:mosesyou1994@gmail.com" 
              className="text-sidebar-foreground/70 hover:text-sidebar-foreground transition-colors"
            >
              <Mail className="size-4" />
            </a>
          </div>
          <SidebarSeparator />
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarGroup>
  )
}

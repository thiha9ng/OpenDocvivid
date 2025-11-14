"use client"

import * as React from "react"
import {
    BadgeCheck,
    ChevronsUpDown,
    LogOut,
    Sparkles,
    Gift,
} from "lucide-react"
import { FaGoogle } from "react-icons/fa"
import { Spinner } from "@/components/ui/spinner"
import {
    Avatar,
    AvatarFallback,
    AvatarImage,
} from "@/components/ui/avatar"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    useSidebar,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import {
    Tooltip,
    TooltipContent,
    TooltipTrigger,
} from "@/components/ui/tooltip"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { signIn, signOut } from "next-auth/react"
import { AccountDialog } from "@/components/account-dialog"
import { useRouter } from "next/navigation"
import { redeemCode } from "@/lib/api"
import { toast } from "sonner"

export function NavUser({
    user,
}: {
    user?: {
        name: string
        email: string
        avatar: string
    } | null
}) {
    const { isMobile, state } = useSidebar()
    const isCollapsed = state === "collapsed"
    const [isLoading, setIsLoading] = React.useState(false)
    const router = useRouter()
    const [accountDialogOpen, setAccountDialogOpen] = React.useState(false)
    const [redeemDialogOpen, setRedeemDialogOpen] = React.useState(false)
    const [redeemCodeInput, setRedeemCodeInput] = React.useState("")
    const [isRedeeming, setIsRedeeming] = React.useState(false)
    
    const signInWithGoogle = async () => {
        setIsLoading(true)
        try {
            await signIn("google")
        } catch (error) {
            console.error("Sign in error:", error)
            setIsLoading(false)
        }
    }

    const handleRedeemCode = async () => {
        if (!redeemCodeInput.trim()) {
            toast.error("Please enter a redeem code")
            return
        }

        setIsRedeeming(true)
        try {
            const result = await redeemCode(redeemCodeInput.trim())
            toast.success(`Successfully redeemed! +${result.data.credit_amount} credits. New balance: ${result.data.balance_after}`)
            setRedeemDialogOpen(false)
            setRedeemCodeInput("")
        } catch (error: any) {
            const errorMessage = error?.message || "Failed to redeem code. Please check the code and try again."
            toast.error(errorMessage)
        } finally {
            setIsRedeeming(false)
        }
    }

    if (!user) {
        return (
            <SidebarMenu>
                <SidebarMenuItem>
                    <Tooltip open={isCollapsed ? undefined : false}>
                        <TooltipTrigger asChild>
                            <Button
                                variant="outline"
                                className="w-full cursor-pointer justify-start h-auto py-3 px-3 hover:bg-sidebar-accent hover:scale-[1.02] transition-all duration-200 group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:p-2"
                                onClick={() => {
                                    // Handle Google sign in
                                    signInWithGoogle()
                                }}
                                disabled={isLoading}
                            >
                                {isLoading ? (
                                    <Spinner className="size-4 text-primary" />
                                ) : (
                                    <FaGoogle className="size-4 text-primary" />
                                )}
                                <span className="group-data-[collapsible=icon]:hidden">
                                    {isLoading ? "Signing in..." : "Sign in with Google"}
                                </span>
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent side="right" sideOffset={8}>
                            <p>Sign in with Google</p>
                        </TooltipContent>
                    </Tooltip>
                </SidebarMenuItem>
            </SidebarMenu>
        )
    }

    // User is logged in, show user menu
    return (
        <SidebarMenu>
            <SidebarMenuItem>
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <SidebarMenuButton
                            size="lg"
                            className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                        >
                            <Avatar className="h-8 w-8 rounded-lg">
                                <AvatarImage src={user.avatar} alt={user.name} />
                                <AvatarFallback className="rounded-lg">CN</AvatarFallback>
                            </Avatar>
                            <div className="grid flex-1 text-left text-sm leading-tight">
                                <span className="truncate font-medium">{user.name}</span>
                                <span className="truncate text-xs">{user.email}</span>
                            </div>
                            <ChevronsUpDown className="ml-auto size-4" />
                        </SidebarMenuButton>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent
                        className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
                        side={isMobile ? "bottom" : "right"}
                        align="end"
                        sideOffset={4}
                    >
                        <DropdownMenuLabel className="p-0 font-normal">
                            <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                                <Avatar className="h-8 w-8 rounded-lg">
                                    <AvatarImage src={user.avatar} alt={user.name} />
                                    <AvatarFallback className="rounded-lg">CN</AvatarFallback>
                                </Avatar>
                                <div className="grid flex-1 text-left text-sm leading-tight">
                                    <span className="truncate font-medium">{user.name}</span>
                                    <span className="truncate text-xs">{user.email}</span>
                                </div>
                            </div>
                        </DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuGroup>
                            <DropdownMenuItem onClick={() => router.push("/pricing")}>
                                <Sparkles />
                                Upgrade to Pro
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => setRedeemDialogOpen(true)}>
                                <Gift />
                                Redeem Code
                            </DropdownMenuItem>
                        </DropdownMenuGroup>
                        <DropdownMenuSeparator />
                        <DropdownMenuGroup>
                            <DropdownMenuItem onClick={() => setAccountDialogOpen(true)}>
                                <BadgeCheck />
                                Account
                            </DropdownMenuItem>
                            {/* <DropdownMenuItem>
                                <CreditCard />
                                Billing
                            </DropdownMenuItem> */}
                        </DropdownMenuGroup>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem asChild>
                            <button
                                type="button"
                                className="w-full flex items-center gap-3 p-3 duration-200 bg-red-500/10 rounded-xl hover:bg-red-500/20 cursor-pointer border border-transparent hover:border-red-500/30 hover:shadow-sm transition-all group"
                                onClick={() => signOut({ callbackUrl: "/" })}
                            >
                                <LogOut className="w-4 h-4 text-red-500 group-hover:text-red-600" />
                                <span className="text-sm font-medium text-red-500 group-hover:text-red-600">
                                    Sign Out
                                </span>
                            </button>
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </SidebarMenuItem>
            {user && (
                <>
                    <AccountDialog
                        open={accountDialogOpen}
                        onOpenChange={setAccountDialogOpen}
                        user={user}
                    />
                    
                    <Dialog open={redeemDialogOpen} onOpenChange={setRedeemDialogOpen}>
                        <DialogContent className="sm:max-w-md">
                            <DialogHeader>
                                <DialogTitle>Redeem Code</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4 py-4">
                                <div className="space-y-2">
                                    <Input
                                        placeholder="Enter redeem code..."
                                        value={redeemCodeInput}
                                        onChange={(e) => setRedeemCodeInput(e.target.value)}
                                        onKeyDown={(e) => {
                                            if (e.key === "Enter" && !isRedeeming) {
                                                handleRedeemCode()
                                            }
                                        }}
                                        disabled={isRedeeming}
                                        className="font-mono"
                                        autoFocus
                                    />
                                </div>
                            </div>
                            <DialogFooter className="sm:justify-end gap-2">
                                <Button
                                    type="button"
                                    onClick={handleRedeemCode}
                                    disabled={isRedeeming || !redeemCodeInput.trim()}
                                    className="gap-2"
                                >
                                    {isRedeeming && <Spinner className="size-4" />}
                                    {isRedeeming ? "Redeeming..." : "Confirm"}
                                </Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                </>
            )}
        </SidebarMenu>
    )
}

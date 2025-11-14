"use client"

import * as React from "react"
import { motion } from "motion/react"
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { ScrollArea } from "@/components/ui/scroll-area"
import { User, CreditCard, Settings, Coins, TrendingUp, TrendingDown, Sun, Moon, Monitor } from "lucide-react"
import { getCreditTransactions } from "@/lib/api/credit"
import { CreditTransaction, TransactionType } from "@/lib/types/api"
import { useTheme } from "next-themes"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"

const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)
    
    if (diffInSeconds < 60) return 'just now'
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`
    if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 604800)} weeks ago`
    if (diffInSeconds < 31536000) return `${Math.floor(diffInSeconds / 2592000)} months ago`
    return `${Math.floor(diffInSeconds / 31536000)} years ago`
}

interface AccountDialogProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    user: {
        name: string
        email: string
        avatar: string
    }
}

const transactionTypeLabels: Record<TransactionType, string> = {
    [TransactionType.MONTHLY_GRANT]: "Monthly Grant",
    [TransactionType.MONTHLY_RECLAIM]: "Monthly Reclaim",
    [TransactionType.TASK_CONSUME]: "Task Consumption",
    [TransactionType.REFUND]: "Refund",
    [TransactionType.ADMIN_ADJUST]: "Admin Adjustment",
    [TransactionType.PURCHASE]: "Purchase",
    [TransactionType.REDEEM]: "Redeem Code",
}

export function AccountDialog({ open, onOpenChange, user }: AccountDialogProps) {
    const [transactions, setTransactions] = React.useState<CreditTransaction[]>([])
    const [currentBalance, setCurrentBalance] = React.useState(0)
    const [loading, setLoading] = React.useState(true)
    const { theme, setTheme } = useTheme()
    const [mounted, setMounted] = React.useState(false)

    React.useEffect(() => {
        setMounted(true)
    }, [])

    React.useEffect(() => {
        if (open) {
            loadTransactions()
        }
    }, [open])

    const loadTransactions = async () => {
        try {
            setLoading(true)
            const response = await getCreditTransactions()
            setTransactions(response.data.transactions)
            setCurrentBalance(response.data.current_balance)
        } catch (error) {
            console.error("Failed to load transactions:", error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-2xl sm:max-w-xl md:max-w-2xl lg:max-w-4xl max-h-[85vh] p-0 gap-0">
                <DialogHeader className="px-6 pt-6 pb-4">
                    <DialogTitle className="text-2xl font-bold">Account Settings</DialogTitle>
                </DialogHeader>
                
                <Tabs defaultValue="subscribe" className="w-full">
                    <div className="px-6 border-b">
                        <TabsList className="w-full justify-start h-12 bg-transparent p-0 gap-6">
                            <TabsTrigger
                                value="profile"
                                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-0 pb-3"
                            >
                                <User className="h-4 w-4 mr-2" />
                                Profile
                            </TabsTrigger>
                            <TabsTrigger
                                value="subscribe"
                                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-0 pb-3"
                            >
                                <CreditCard className="h-4 w-4 mr-2" />
                                Subscribe
                            </TabsTrigger>
                            <TabsTrigger
                                value="settings"
                                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-0 pb-3"
                            >
                                <Settings className="h-4 w-4 mr-2" />
                                Settings
                            </TabsTrigger>
                        </TabsList>
                    </div>

                    <ScrollArea className="h-[calc(85vh-140px)]">
                        <div className="p-6">
                            <TabsContent value="profile" className="mt-0">
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.3 }}
                                >
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Profile Information</CardTitle>
                                            <CardDescription>Your account details</CardDescription>
                                        </CardHeader>
                                        <CardContent className="space-y-4">
                                            <div className="flex items-center gap-4">
                                                <div className="h-20 w-20 rounded-full overflow-hidden bg-muted">
                                                    <img src={user.avatar} alt={user.name} className="h-full w-full object-cover" />
                                                </div>
                                                <div>
                                                    <p className="text-lg font-semibold">{user.name}</p>
                                                    <p className="text-sm text-muted-foreground">{user.email}</p>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </motion.div>
                            </TabsContent>

                            <TabsContent value="subscribe" className="mt-0">
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.3 }}
                                    className="space-y-6"
                                >
                                    {/* Current Balance Card */}
                                    <Card className="border-2 border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
                                        <CardHeader>
                                            <CardTitle className="flex items-center gap-2">
                                                <Coins className="h-5 w-5 text-primary" />
                                                Current Balance
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            {loading ? (
                                                <Skeleton className="h-12 w-32" />
                                            ) : (
                                                <div className="flex items-baseline gap-2">
                                                    <span className="text-4xl font-bold text-primary">{currentBalance}</span>
                                                    <span className="text-lg text-muted-foreground">credits</span>
                                                </div>
                                            )}
                                        </CardContent>
                                    </Card>

                                    {/* Subscription Level Card */}
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Subscription Level</CardTitle>
                                            <CardDescription>Your current plan</CardDescription>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-3">
                                                    <Badge variant="secondary" className="text-base px-4 py-1">
                                                        Free Plan
                                                    </Badge>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>

                                    {/* Transaction History */}
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Transaction History</CardTitle>
                                            <CardDescription>Your credit transaction details</CardDescription>
                                        </CardHeader>
                                        <CardContent>
                                            {loading ? (
                                                <div className="space-y-3">
                                                    {[1, 2, 3, 4, 5].map((i) => (
                                                        <div key={i} className="flex items-center gap-4">
                                                            <Skeleton className="h-10 w-10 rounded-full" />
                                                            <div className="flex-1 space-y-2">
                                                                <Skeleton className="h-4 w-40" />
                                                                <Skeleton className="h-3 w-24" />
                                                            </div>
                                                            <Skeleton className="h-6 w-16" />
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : transactions?.length === 0 ? (
                                                <div className="text-center py-8 text-muted-foreground">
                                                    <Coins className="h-12 w-12 mx-auto mb-3 opacity-30" />
                                                    <p>No transactions yet</p>
                                                </div>
                                            ) : (
                                                <div className="space-y-1">
                                                    {transactions.map((transaction, index) => {
                                                        const isPositive = transaction.amount > 0
                                                        return (
                                                            <motion.div
                                                                key={transaction.id}
                                                                initial={{ opacity: 0, x: -10 }}
                                                                animate={{ opacity: 1, x: 0 }}
                                                                transition={{ delay: index * 0.05, duration: 0.2 }}
                                                                className="flex items-center justify-between py-3 px-4 rounded-lg hover:bg-muted/50 transition-colors"
                                                            >
                                                                <div className="flex items-center gap-3 flex-1">
                                                                    <div className={`h-10 w-10 rounded-full flex items-center justify-center ${
                                                                        isPositive ? 'bg-green-500/10' : 'bg-red-500/10'
                                                                    }`}>
                                                                        {isPositive ? (
                                                                            <TrendingUp className="h-5 w-5 text-green-600" />
                                                                        ) : (
                                                                            <TrendingDown className="h-5 w-5 text-red-600" />
                                                                        )}
                                                                    </div>
                                                                    <div className="flex-1 min-w-0">
                                                                        <p className="font-medium text-sm">
                                                                            {transactionTypeLabels[transaction.transaction_type]}
                                                                        </p>
                                                                        <p className="text-xs text-muted-foreground truncate">
                                                                            {transaction.description}
                                                                        </p>
                                                                        <p className="text-xs text-muted-foreground mt-1">
                                                                            {formatTimeAgo(transaction.created_at)}
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                                <div className="text-right ml-4">
                                                                    <p className={`font-semibold text-base ${
                                                                        isPositive ? 'text-green-600' : 'text-red-600'
                                                                    }`}>
                                                                        {isPositive ? '+' : ''}{transaction.amount}
                                                                    </p>
                                                                    <p className="text-xs text-muted-foreground">
                                                                        Balance: {transaction.balance_after}
                                                                    </p>
                                                                </div>
                                                            </motion.div>
                                                        )
                                                    })}
                                                </div>
                                            )}
                                        </CardContent>
                                    </Card>
                                </motion.div>
                            </TabsContent>

                            <TabsContent value="settings" className="mt-0">
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.3 }}
                                >
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>General Settings</CardTitle>
                                            <CardDescription>Manage your preferences</CardDescription>
                                        </CardHeader>
                                        <CardContent className="space-y-6">
                                            {/* Website Language */}
                                            {/* <div className="space-y-2">
                                                <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                                    Website language
                                                </label>
                                                <Select defaultValue="en" disabled>
                                                    <SelectTrigger className="w-full">
                                                        <SelectValue placeholder="Select language" />
                                                    </SelectTrigger>
                                                    <SelectContent>
                                                        <SelectItem value="en">English</SelectItem>
                                                    </SelectContent>
                                                </Select>
                                            </div> */}

                                            {/* Theme Selection */}
                                            <div className="space-y-2">
                                                <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                                    Theme
                                                </label>
                                                {mounted ? (
                                                    <Select value={theme} onValueChange={setTheme}>
                                                        <SelectTrigger className="w-full">
                                                            <SelectValue placeholder="Select theme" />
                                                        </SelectTrigger>
                                                        <SelectContent>
                                                            <SelectItem value="system">
                                                                <div className="flex items-center gap-2">
                                                                    <Monitor className="h-4 w-4" />
                                                                    <span>System</span>
                                                                </div>
                                                            </SelectItem>
                                                            <SelectItem value="light">
                                                                <div className="flex items-center gap-2">
                                                                    <Sun className="h-4 w-4" />
                                                                    <span>Light</span>
                                                                </div>
                                                            </SelectItem>
                                                            <SelectItem value="dark">
                                                                <div className="flex items-center gap-2">
                                                                    <Moon className="h-4 w-4" />
                                                                    <span>Dark</span>
                                                                </div>
                                                            </SelectItem>
                                                        </SelectContent>
                                                    </Select>
                                                ) : (
                                                    <Skeleton className="h-9 w-full" />
                                                )}
                                            </div>
                                        </CardContent>
                                    </Card>
                                </motion.div>
                            </TabsContent>
                        </div>
                    </ScrollArea>
                </Tabs>
            </DialogContent>
        </Dialog>
    )
}


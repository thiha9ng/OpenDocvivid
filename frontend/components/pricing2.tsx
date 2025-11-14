"use client";

import { ArrowRight, CircleCheck, Loader2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { createSubscriptionPayment } from "@/lib/api/credit";
import { SubscriptionType, SubscriptionPeriod } from "@/lib/types/api";

interface PricingFeature {
  text: string;
}

interface PricingPlan {
  id: string;
  name: string;
  description: string;
  monthlyPrice: string;
  yearlyPrice: string;
  monthlyProductId: string;
  yearlyProductId: string;
  features: PricingFeature[];
  button: {
    text: string;
    url: string;
  };
}

interface Pricing2Props {
  heading?: string;
  description?: string;
  plans?: PricingPlan[];
}

const Pricing2 = ({
  heading = "Pricing",
  description = "Check out our affordable pricing plans",
  plans = [
    {
      id: "plus",
      name: "Plus",
      description: "For personal use",
      monthlyPrice: "$19",
      yearlyPrice: "$15",
      monthlyProductId: "",
      yearlyProductId: "",
      features: [
        { text: "Up to 5 team members" },
        { text: "Basic components library" },
        { text: "Community support" },
        { text: "1GB storage space" },
      ],
      button: {
        text: "Purchase",
        url: "https://www.shadcnblocks.com",
      },
    },
    {
      id: "pro",
      name: "Pro",
      description: "For professionals",
      monthlyPrice: "$49",
      yearlyPrice: "$35",
      monthlyProductId: "",
      yearlyProductId: "",
      features: [
        { text: "Unlimited team members" },
        { text: "Advanced components" },
        { text: "Priority support" },
        { text: "Unlimited storage" },
      ],
      button: {
        text: "Purchase",
        url: "https://www.shadcnblocks.com",
      },
    },
  ],
}: Pricing2Props) => {
  const [isYearly, setIsYearly] = useState(false);
  const [loadingPlanId, setLoadingPlanId] = useState<string | null>(null);

  const handlePurchase = async (plan: PricingPlan) => {
    try {
      setLoadingPlanId(plan.id);
      
      const productId = isYearly ? plan.yearlyProductId : plan.monthlyProductId;
      const subscriptionType = plan.id as SubscriptionType;
      const subscriptionPeriod = isYearly ? SubscriptionPeriod.YEARLY : SubscriptionPeriod.MONTHLY;

      if (!productId) {
        toast.error("Product ID not available. Please try again.");
        return;
      }

      const response = await createSubscriptionPayment(
        productId,
        subscriptionType,
        subscriptionPeriod
      );

      if (response.data && response.data.payment_url) {
        // Open payment URL in a new tab
        window.open(response.data.payment_url, "_blank");
      } else {
        toast.error("Failed to get payment URL. Please try again.");
      }
    } catch (error) {
      console.error("Failed to create payment:", error);
      toast.error("Failed to process payment. Please try again.");
    } finally {
      setLoadingPlanId(null);
    }
  };
  return (
    <section className="py-32">
      <div className="container">
        <div className="mx-auto flex max-w-5xl flex-col items-center gap-6 text-center">
          <h2 className="text-pretty text-3xl font-bold lg:text-5xl">
            {heading}
          </h2>
          <p className="text-muted-foreground lg:text-xl">{description}</p>
          <div className="flex items-center gap-3 text-lg">
            Monthly
            <Switch
              checked={isYearly}
              onCheckedChange={() => setIsYearly(!isYearly)}
            />
            Yearly
          </div>
          <div className="flex flex-col items-stretch gap-6 md:flex-row md:justify-center">
            {plans.map((plan) => (
              <Card
                key={plan.id}
                className="flex w-100 flex-col justify-between text-left"
              >
                <CardHeader>
                  <CardTitle>
                    <p>{plan.name}</p>
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {plan.description}
                  </p>
                  <span className="text-4xl font-bold">
                    {isYearly ? plan.yearlyPrice : plan.monthlyPrice}
                  </span>
                  <p className="text-muted-foreground">
                    Billed{" "}
                    {isYearly
                      ? `$${Number(plan.yearlyPrice.slice(1)) * 12}`
                      : `$${Number(plan.monthlyPrice.slice(1)) * 12}`}{" "}
                    annually
                  </p>
                </CardHeader>
                <CardContent>
                  <Separator className="mb-6" />
                  <ul className="space-y-4">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-center gap-2">
                        <CircleCheck className="size-4" />
                        <span>{feature.text}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
                <CardFooter className="mt-auto">
                  <Button 
                    className="w-full cursor-pointer" 
                    onClick={() => handlePurchase(plan)}
                    disabled={loadingPlanId !== null}
                  >
                    {loadingPlanId === plan.id ? (
                      <>
                        <Loader2 className="mr-2 size-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        {plan.button.text}
                        <ArrowRight className="ml-2 size-4" />
                      </>
                    )}
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export { Pricing2 };

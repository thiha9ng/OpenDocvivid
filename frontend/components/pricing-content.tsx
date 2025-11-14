"use client";

import { useEffect, useState } from "react";
import { Pricing2 } from "@/components/pricing2";
import { getSubscriptionPlans } from "@/lib/api";
import { SubscriptionPlan } from "@/lib/types/api";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

interface PricingPlan {
  id: string;
  name: string;
  description: string;
  monthlyPrice: string;
  yearlyPrice: string;
  monthlyProductId: string;
  yearlyProductId: string;
  features: { text: string }[];
  button: {
    text: string;
    url: string;
  };
}

// Feature mapping based on plan type and credits
function getPlanFeatures(plan: SubscriptionPlan): { text: string }[] {
  const features: { text: string }[] = [];
  
  // Add credits info
  if (plan.monthly_credits > 0) {
    features.push({ text: `${plan.monthly_credits} credits per month` });
  } else {
    features.push({ text: "No credits" });
  }

  // Features for Basic plan
  if (plan.type === "basic") {
    features.push(
      { text: "Generate ~5 videos up to 3 minutes" },
      { text: "Create from text, URL, or files" },
      { text: "No watermark" },
      { text: "1 concurrent video task" },
      { text: "20+ voice options" }
    );
  }

  // Features for Pro plan
  if (plan.type === "pro") {
    features.push(
      { text: "Generate ~12 videos up to 3 minutes" },
      { text: "Create from text, URL, or files" },
      { text: "No watermark" },
      { text: "2 concurrent video tasks" },
      { text: "20+ voice options" }
    );
  }

  // Features for Enterprise plan
  if (plan.type === "enterprise") {
    features.push(
      { text: "8K video quality" },
      { text: "Custom AI voice cloning" },
      { text: "Dedicated infrastructure" },
      { text: "White-label solution" },
      { text: "Advanced API access" },
      { text: "Unlimited cloud storage" },
      { text: "Real-time analytics dashboard" },
      { text: "24/7 dedicated support" },
      { text: "Custom integrations" },
      { text: "SLA guarantees" }
    );
  }

  return features;
}

// Convert API plan to Pricing2 component format
function convertToPricingPlan(plan: SubscriptionPlan): PricingPlan {
  const monthlyPeriod = plan.periods.find((p) => p.period === "monthly");
  const yearlyPeriod = plan.periods.find((p) => p.period === "yearly");

  return {
    id: plan.type,
    name: plan.name,
    description: plan.description,
    monthlyPrice: monthlyPeriod ? `$${monthlyPeriod.price}` : "$0",
    yearlyPrice: yearlyPeriod ? `$${yearlyPeriod.price}` : "$0",
    monthlyProductId: monthlyPeriod?.product_id || "",
    yearlyProductId: yearlyPeriod?.product_id || "",
    features: getPlanFeatures(plan),
    button: {
      text: "Subscribe",
      url: "/api/auth/signin",
    },
  };
}

// Loading skeleton component
function PricingSkeleton() {
  return (
    <section className="py-32">
      <div className="container">
        <div className="mx-auto flex max-w-5xl flex-col items-center gap-6 text-center">
          <Skeleton className="h-16 w-96" />
          <Skeleton className="h-8 w-[600px]" />
          <Skeleton className="h-12 w-48 mt-4" />
          <div className="flex flex-col items-stretch gap-6 md:flex-row md:justify-center mt-6">
            {[1, 2].map((i) => (
              <Card key={i} className="w-80">
                <CardHeader>
                  <Skeleton className="h-8 w-24 mb-2" />
                  <Skeleton className="h-4 w-40 mb-4" />
                  <Skeleton className="h-12 w-32 mb-2" />
                  <Skeleton className="h-4 w-48" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[1, 2, 3, 4, 5].map((j) => (
                      <Skeleton key={j} className="h-6 w-full" />
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

export function PricingContent() {
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPlans() {
      try {
        setLoading(true);
        const response = await getSubscriptionPlans();
        
        if (response.data && response.data.plans) {
          const convertedPlans = response.data.plans
            .filter((plan) => plan.type === "basic" || plan.type === "pro")
            .map(convertToPricingPlan);
          setPlans(convertedPlans);
        }
      } catch (err) {
        console.error("Failed to fetch subscription plans:", err);
        setError("Failed to load pricing plans. Please try again later.");
      } finally {
        setLoading(false);
      }
    }

    fetchPlans();
  }, []);

  if (loading) {
    return <PricingSkeleton />;
  }

  if (error) {
    return (
      <section className="py-32">
        <div className="container">
          <div className="mx-auto flex max-w-5xl flex-col items-center gap-6 text-center">
            <h2 className="text-4xl font-bold text-destructive">
              Unable to Load Pricing
            </h2>
            <p className="text-muted-foreground">{error}</p>
          </div>
        </div>
      </section>
    );
  }

  if (plans.length === 0) {
    return (
      <section className="py-32">
        <div className="container">
          <div className="mx-auto flex max-w-5xl flex-col items-center gap-6 text-center">
            <h2 className="text-4xl font-bold">No Plans Available</h2>
            <p className="text-muted-foreground">
              Please check back later for pricing information.
            </p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <Pricing2
      heading="Choose Your Plan"
      description="Transform your technical documentation into engaging AI-powered videos with flexible pricing options"
      plans={plans}
    />
  );
}


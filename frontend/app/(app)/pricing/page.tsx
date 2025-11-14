import { Metadata } from "next";
import { PricingContent } from "@/components/pricing-content";

export const metadata: Metadata = {
    title: "Pricing Plans | DocVivid - Technical Documentation Video Creator",
    description: "Choose the perfect plan for converting your technical documentation into professional AI videos. Special pricing for developers, engineering teams, and technical writers.",
    keywords: ["technical video pricing", "developer documentation tools", "API documentation video pricing", "technical content creation cost", "code explanation video plans"],
};

export default function PricingPage() {
    return <div className="mx-auto max-w-7xl">
        <PricingContent />
    </div>
}
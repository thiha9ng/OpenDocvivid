import { Metadata } from "next"
import ExploreContent from "@/components/explore-content"

export const metadata: Metadata = {
    title: "Explore AI Video Templates | DocVivid - Technical Documentation Video Creator",
    description: "Browse our library of technical documentation video templates for developers, engineers, and technical writers. Convert your code, API docs, and technical guides into professional videos.",
    keywords: ["technical documentation templates", "developer video templates", "code explanation videos", "API documentation templates", "technical video examples"],
}

export default function ExplorePage() {
    return <ExploreContent />
}
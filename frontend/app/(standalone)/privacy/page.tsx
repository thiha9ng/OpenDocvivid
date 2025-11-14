"use client"

import React from "react"
import { motion } from "motion/react"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header with back button */}
      <div className="border-b">
        <div className="container mx-auto px-4 py-4">
          <Link 
            href="/"
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors rounded-md hover:bg-accent"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Home
          </Link>
        </div>
      </div>

      {/* Main content */}
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="prose prose-gray dark:prose-invert max-w-none"
        >
          <h1 className="text-4xl font-bold mb-8">Privacy Policy</h1>
          
          <p className="text-muted-foreground mb-8">Last updated: 2025-11-07</p>

          <div className="space-y-8">
            <section>
              <p>
                [OpenRopic] (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;), a company registered in Singapore, operates the SaaS platform at aidocvivid.com (the &quot;Service&quot;). We are committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use the Service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">1. Information We Collect</h2>
              
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium mb-2">1.1 Personal Data</h3>
                  <p>When you register, subscribe, or contact us, we collect:</p>
                  <ul className="list-disc pl-6 space-y-1 mt-2">
                    <li>Name, email address, billing information, and payment details.</li>
                    <li>Company name and business contact details (if applicable).</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium mb-2">1.2 Usage Data</h3>
                  <p>We automatically collect:</p>
                  <ul className="list-disc pl-6 space-y-1 mt-2">
                    <li>IP address, browser type, device information, and operating system.</li>
                    <li>Pages visited, time spent, features used, and referral sources.</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-medium mb-2">1.3 User Content</h3>
                  <p>Any documents, files, or data you upload, process, or generate using the Service.</p>
                </div>

                <div>
                  <h3 className="text-lg font-medium mb-2">1.4 Cookies and Tracking</h3>
                  <p>We use cookies, pixels, and similar technologies to:</p>
                  <ul className="list-disc pl-6 space-y-1 mt-2">
                    <li>Authenticate users and maintain sessions.</li>
                    <li>Analyze usage and improve the Service.</li>
                    <li>Deliver personalized features.</li>
                  </ul>
                  <p className="mt-2">You can manage cookie preferences via your browser settings.</p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">2. How We Use Your Information</h2>
              <p>We use collected information to:</p>
              <ul className="list-disc pl-6 space-y-1 mt-2">
                <li>Provide, operate, and maintain the Service.</li>
                <li>Process payments and manage subscriptions.</li>
                <li>Communicate with you about updates, support, and billing.</li>
                <li>Improve functionality, security, and user experience.</li>
                <li>Detect and prevent fraud, abuse, or violations of our Terms.</li>
                <li>Comply with legal obligations.</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">3. Disclosure of Your Information</h2>
              <p className="mb-4">We do not sell your personal data. We may share it with:</p>
              
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium mb-2">3.1 Service Providers</h3>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Payment processors (e.g., Stripe).</li>
                    <li>Cloud hosting and infrastructure providers.</li>
                    <li>Analytics and monitoring tools.</li>
                  </ul>
                  <p className="mt-2">All under strict confidentiality and data processing agreements.</p>
                </div>

                <div>
                  <h3 className="text-lg font-medium mb-2">3.2 Legal Requirements</h3>
                  <p>When required by law, regulation, or court order in Singapore or other jurisdictions with lawful authority.</p>
                </div>

                <div>
                  <h3 className="text-lg font-medium mb-2">3.3 Business Transfers</h3>
                  <p>In the event of merger, acquisition, or asset sale, your data may be transferred as part of the transaction.</p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">4. Data Security</h2>
              <p>We implement industry-standard security measures, including:</p>
              <ul className="list-disc pl-6 space-y-1 mt-2">
                <li>Encryption of data in transit (TLS) and at rest (AES-256).</li>
                <li>Access controls and regular security audits.</li>
                <li>Secure development practices.</li>
              </ul>
              <p className="mt-4">However, no method of transmission or storage is 100% secure. We cannot guarantee absolute security.</p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">5. Data Retention</h2>
              <p>We retain your personal data only as long as necessary:</p>
              <ul className="list-disc pl-6 space-y-1 mt-2">
                <li>For active accounts: during your subscription and for 12 months after termination (for billing and support).</li>
                <li>For legal compliance: up to 7 years as required under Singapore tax and corporate law.</li>
                <li>Anonymized usage data may be retained indefinitely for analytics.</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">6. Your Rights (Singapore PDPA Compliance)</h2>
              <p>Under the Personal Data Protection Act 2012 (PDPA), you have the right to:</p>
              <ul className="list-disc pl-6 space-y-1 mt-2">
                <li>Access your personal data we hold.</li>
                <li>Request correction of inaccurate data.</li>
                <li>Withdraw consent for non-essential processing (may affect Service use).</li>
                <li>Request deletion (subject to legal retention obligations).</li>
              </ul>
              <p className="mt-4">To exercise these rights, contact us at [Insert Email Address]. We respond within 30 days.</p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">7. International Data Transfers</h2>
              <p>
                Your data may be processed in Singapore, the United States, or other countries where our service providers operate. We ensure appropriate safeguards (e.g., Standard Contractual Clauses) are in place for cross-border transfers.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">8. Third-Party Links</h2>
              <p>
                The Service may contain links to third-party websites. We are not responsible for their privacy practices. Review their policies separately.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">9. Children&apos;s Privacy</h2>
              <p>
                The Service is not intended for individuals under 18. We do not knowingly collect data from children.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">10. Changes to This Policy</h2>
              <p>
                We may update this Privacy Policy at any time. Changes will be posted on this page with the updated date. Continued use of the Service after changes constitutes acceptance.
              </p>
            </section>
          </div>
        </motion.div>
      </div>
    </div>
  )
}


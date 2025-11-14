"use client"

import React from "react"
import { motion } from "motion/react"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"

export default function TermsPage() {
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
          <h1 className="text-4xl font-bold mb-8">Terms of Service</h1>
          
          <p className="text-muted-foreground mb-8">Last updated: 2025-11-07</p>

          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-semibold mb-4">1. Acceptance of Terms</h2>
              <p>
                By accessing or using aidocvivid.com (the &quot;Service&quot;), operated by [OpenRopic], 
                a company registered in Singapore (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;), you agree to be bound by 
                these Terms of Service (&quot;Terms&quot;). If you do not agree, do not use the Service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">2. Eligibility</h2>
              <p>
                You must be at least 18 years old and capable of forming a binding contract to use 
                the Service. By using the Service, you represent that you meet these requirements.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">3. Account Registration</h2>
              <p>
                To access certain features, you must create an account with accurate information. 
                You are responsible for maintaining the confidentiality of your login credentials 
                and for all activities under your account. Notify us immediately of any unauthorized use.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">4. Subscription and Payment</h2>
              <div className="space-y-3">
                <p>
                  <strong>4.1</strong> The Service is provided on a subscription basis. You will be 
                  charged the fees displayed at signup (&quot;Fees&quot;) via the chosen payment method.
                </p>
                <p>
                  <strong>4.2</strong> Subscriptions auto-renew unless cancelled at least 48 hours 
                  before the renewal date. No refunds for partial months.
                </p>
                <p>
                  <strong>4.3</strong> We may change Fees with 30 days&apos; notice. Continued use after 
                  changes constitutes acceptance.
                </p>
                <p>
                  <strong>4.4</strong> All payments are processed through third-party providers. 
                  You authorize us to charge your payment method.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">5. Use of the Service</h2>
              <div className="space-y-3">
                <p>
                  <strong>5.1</strong> You may use the Service only for lawful purposes and in 
                  accordance with these Terms.
                </p>
                <p>
                  <strong>5.2</strong> Prohibited activities include:
                </p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Reverse engineering, copying, or modifying the Service.</li>
                  <li>Using the Service to infringe intellectual property rights.</li>
                  <li>Transmitting viruses, spam, or harmful code.</li>
                  <li>Interfering with the Service&apos;s operation.</li>
                </ul>
                <p>
                  <strong>5.3</strong> We may suspend or terminate your access without notice for violations.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">6. Intellectual Property</h2>
              <div className="space-y-3">
                <p>
                  <strong>6.1</strong> The Service, including all content, features, and functionality, 
                  is owned by us or our licensors and protected by Singapore and international copyright, 
                  trademark, and other laws.
                </p>
                <p>
                  <strong>6.2</strong> You retain ownership of content you upload (&quot;User Content&quot;), 
                  but grant us a worldwide, royalty-free, perpetual license to use, modify, and 
                  display it to provide the Service.
                </p>
                <p>
                  <strong>6.3</strong> You represent that your User Content does not infringe 
                  third-party rights.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">7. User Content</h2>
              <div className="space-y-3">
                <p>
                  <strong>7.1</strong> You are solely responsible for your User Content.
                </p>
                <p>
                  <strong>7.2</strong> We may remove any User Content that violates these Terms 
                  or is otherwise objectionable.
                </p>
                <p>
                  <strong>7.3</strong> We do not endorse or guarantee the accuracy of User Content.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">8. Termination</h2>
              <div className="space-y-3">
                <p>
                  <strong>8.1</strong> You may terminate your account at any time via settings.
                </p>
                <p>
                  <strong>8.2</strong> We may terminate or suspend your access immediately, without 
                  notice, for breach of these Terms or if required by law.
                </p>
                <p>
                  <strong>8.3</strong> Upon termination, your right to use the Service ceases. 
                  Sections 6, 9, 10, 11, and 13 survive.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">9. Disclaimer of Warranties</h2>
              <p className="uppercase font-medium">
                THE SERVICE IS PROVIDED &quot;AS IS&quot; AND &quot;AS AVAILABLE&quot; WITHOUT WARRANTIES OF ANY KIND, 
                EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO MERCHANTABILITY, FITNESS FOR A 
                PARTICULAR PURPOSE, OR NON-INFRINGEMENT. WE DO NOT WARRANT UNINTERRUPTED, ERROR-FREE, 
                OR VIRUS-FREE OPERATION.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">10. Limitation of Liability</h2>
              <p className="uppercase font-medium mb-3">TO THE MAXIMUM EXTENT PERMITTED BY LAW:</p>
              <div className="space-y-3">
                <p className="uppercase">
                  <strong>10.1</strong> WE SHALL NOT BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, 
                  CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING LOSS OF PROFITS, DATA, OR GOODWILL.
                </p>
                <p className="uppercase">
                  <strong>10.2</strong> OUR TOTAL LIABILITY SHALL NOT EXCEED THE AMOUNT YOU PAID 
                  US IN THE 12 MONTHS PRECEDING THE CLAIM.
                </p>
                <p className="uppercase">
                  <strong>10.3</strong> THESE LIMITATIONS APPLY REGARDLESS OF THE LEGAL THEORY 
                  AND EVEN IF WE WERE ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">11. Indemnification</h2>
              <p>
                You agree to indemnify and hold us, our affiliates, officers, and employees harmless 
                from any claims, losses, damages, liabilities, and expenses (including legal fees) 
                arising from your use of the Service, violation of these Terms, or infringement of 
                third-party rights.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">12. Governing Law and Dispute Resolution</h2>
              <div className="space-y-3">
                <p>
                  <strong>12.1</strong> These Terms are governed by the laws of Singapore, without 
                  regard to conflict of law principles.
                </p>
                <p>
                  <strong>12.2</strong> Any dispute arising from these Terms or the Service shall 
                  be resolved exclusively in the courts of Singapore.
                </p>
                <p>
                  <strong>12.3</strong> You agree to submit to the personal jurisdiction of such courts.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">13. Changes to Terms</h2>
              <p>
                We may update these Terms at any time. Changes will be posted on the Service with 
                the updated date. Continued use after changes constitutes acceptance. Review periodically.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">14. Miscellaneous</h2>
              <div className="space-y-3">
                <p>
                  <strong>14.1</strong> These Terms constitute the entire agreement between you and us.
                </p>
                <p>
                  <strong>14.2</strong> If any provision is unenforceable, the remainder remains in effect.
                </p>
                <p>
                  <strong>14.3</strong> No waiver of any term shall be deemed a further waiver.
                </p>
                <p>
                  <strong>14.4</strong> We may assign these Terms; you may not without our consent.
                </p>
                <p>
                  <strong>14.5</strong> Force majeure: We are not liable for delays due to events 
                  beyond our control.
                </p>
              </div>
            </section>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
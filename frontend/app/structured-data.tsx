"use client";

export default function StructuredData() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "DocVivid",
            "applicationCategory": "DeveloperApplication",
            "offers": {
              "@type": "Offer",
              "price": "0",
              "priceCurrency": "USD"
            },
            "operatingSystem": "Web",
            "description": "Transform technical documentation into engaging AI-narrated videos in minutes. Perfect for developers, tech writers, and educators.",
            "aggregateRating": {
              "@type": "AggregateRating",
              "ratingValue": "4.8",
              "ratingCount": "156"
            }
          })
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
              {
                "@type": "Question",
                "name": "What types of technical documentation can DocVivid convert to video?",
                "acceptedAnswer": {
                  "@type": "Answer",
                  "text": "DocVivid can convert various types of technical documentation including API documentation, code explanations, technical guides, programming tutorials, software documentation, and technical specifications into professional AI-narrated videos."
                }
              },
              {
                "@type": "Question",
                "name": "How long does it take to convert technical documentation to video?",
                "acceptedAnswer": {
                  "@type": "Answer",
                  "text": "DocVivid converts most technical documentation into video in just minutes, depending on the length and complexity of your content. Our AI processes your documentation quickly while maintaining high quality output."
                }
              },
              {
                "@type": "Question",
                "name": "Can I customize the voice and visuals in my technical videos?",
                "acceptedAnswer": {
                  "@type": "Answer",
                  "text": "Yes, DocVivid offers multiple professional voice options and customizable visual templates specifically designed for technical content, code explanations, and developer documentation."
                }
              }
            ]
          })
        }}
      />
    </>
  );
}

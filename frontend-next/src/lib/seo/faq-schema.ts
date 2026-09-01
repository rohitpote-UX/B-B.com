/**
 * Brand Battle — Schema.org FAQPage Builder
 * Builds validated FAQPage JSON-LD schemas based on real, factual product questions and answers.
 */

import { FaqItem } from './seo-types'

export function buildFaqSchema(faqs: FaqItem[]): Record<string, unknown> | undefined {
  if (!faqs || faqs.length === 0) {
    return undefined
  }

  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map(faq => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer,
      },
    })),
  }
}

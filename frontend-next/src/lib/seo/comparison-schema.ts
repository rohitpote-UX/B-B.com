/**
 * Brand Battle — Schema.org Comparison Graph Builder
 * Connects WebPage, BreadcrumbList, two Product entities, and FAQPage into a cohesive JSON-LD graph.
 */

import { ComparisonJsonLdProps } from './seo-types'
import { buildBreadcrumbSchema } from './breadcrumb-schema'
import { buildProductSchema } from './product-schema'

export function buildComparisonSchema({
  product1,
  product2,
  canonicalUrl,
  breadcrumbs,
  faqs,
}: ComparisonJsonLdProps): Record<string, unknown> {
  const p1Schema = buildProductSchema(product1)
  const p2Schema = buildProductSchema(product2)
  const breadcrumbsSchema = buildBreadcrumbSchema(breadcrumbs)

  const graphNodes: Record<string, unknown>[] = [
    {
      '@type': 'WebPage',
      '@id': `${canonicalUrl}#webpage`,
      url: canonicalUrl,
      name: `${product1.name} vs ${product2.name} Comparison & Decision Guide`,
      description: `Comprehensive side-by-side comparison of ${product1.name} and ${product2.name}.`,
    },
    breadcrumbsSchema,
    p1Schema,
    p2Schema,
  ]

  if (faqs && faqs.length > 0) {
    graphNodes.push({
      '@type': 'FAQPage',
      mainEntity: faqs.map(faq => ({
        '@type': 'Question',
        name: faq.question,
        acceptedAnswer: {
          '@type': 'Answer',
          text: faq.answer,
        },
      })),
    })
  }

  return {
    '@context': 'https://schema.org',
    '@graph': graphNodes,
  }
}

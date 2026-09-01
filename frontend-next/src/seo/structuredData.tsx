import React from 'react'

export interface StructuredDataProps {
  jsonLd?: Record<string, unknown> | null
}

export default function StructuredDataScript({ jsonLd }: StructuredDataProps) {
  if (!jsonLd) return null

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  )
}

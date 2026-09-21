import React from 'react'

/**
 * Brand Battle — Premium Editorial Hardware Fallback
 * SVG vector image styled in BrandBattle's signature dark aesthetic (#050505 / #ff1695).
 */
export const FALLBACK_PRODUCT_IMAGE =
  'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600" fill="%23050505"><rect width="600" height="600" fill="%230c0c0e" rx="24"/><rect x="40" y="40" width="520" height="520" fill="none" stroke="%23ffffff" stroke-opacity="0.06" stroke-width="2" rx="16"/><circle cx="300" cy="270" r="70" fill="%23ff1695" fill-opacity="0.08" stroke="%23ff1695" stroke-opacity="0.25" stroke-width="2"/><circle cx="300" cy="270" r="24" fill="none" stroke="%23ff1695" stroke-width="2" stroke-dasharray="4 4"/><path d="M290 270 h20 M300 260 v20" stroke="%23ff1695" stroke-width="2" stroke-linecap="round"/><text x="50%" y="390" dominant-baseline="middle" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-size="13" font-weight="600" letter-spacing="2" fill="%23ffffff" fill-opacity="0.65">BRAND BATTLE HARDWARE</text><text x="50%" y="416" dominant-baseline="middle" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-size="10" letter-spacing="1.5" fill="%23ffffff" fill-opacity="0.35">OFFICIAL INTEL ACTIVE</text></svg>'

/**
 * Graceful onError handler for <img> tags.
 * Prevents browser broken-image placeholder from ever rendering.
 */
export function handleProductImageError(
  e: React.SyntheticEvent<HTMLImageElement, Event>,
  customFallback?: string
) {
  const target = e.currentTarget
  const fallback = customFallback || FALLBACK_PRODUCT_IMAGE
  if (target.src !== fallback) {
    target.onerror = null // Prevent infinite error loops
    target.src = fallback
  }
}

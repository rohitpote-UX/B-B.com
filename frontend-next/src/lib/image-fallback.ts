import React from 'react'

/**
 * Brand Battle — Premium Editorial Hardware Fallback
 * SVG vector image styled in BrandBattle's signature dark aesthetic (#050505 / #ff1695).
 */
export const FALLBACK_PRODUCT_IMAGE =
  "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='600' height='600' viewBox='0 0 600 600' fill='%23050505'><rect width='600' height='600' fill='%230c0c0e' rx='24'/><rect x='40' y='40' width='520' height='520' fill='none' stroke='%23ffffff' stroke-opacity='0.06' stroke-width='2' rx='16'/><circle cx='300' cy='270' r='70' fill='%23ff1695' fill-opacity='0.08' stroke='%23ff1695' stroke-opacity='0.25' stroke-width='2'/><circle cx='300' cy='270' r='24' fill='none' stroke='%23ff1695' stroke-width='2' stroke-dasharray='4 4'/><path d='M290 270 h20 M300 260 v20' stroke='%23ff1695' stroke-width='2' stroke-linecap='round'/><text x='50%' y='390' dominant-baseline='middle' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif' font-size='13' font-weight='600' letter-spacing='2' fill='%23ffffff' fill-opacity='0.65'>BRAND BATTLE HARDWARE</text><text x='50%' y='416' dominant-baseline='middle' text-anchor='middle' font-family='-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif' font-size='10' letter-spacing='1.5' fill='%23ffffff' fill-opacity='0.35'>OFFICIAL INTEL ACTIVE</text></svg>"

/**
 * Known quarantined mismatched image signatures mapped to their actual model.
 */
export const QUARANTINED_IMAGE_SIGNATURES: Record<string, { brand: string; generation: string; actualModel: string }> = {
  '71j8tz0uejl': { brand: 'samsung', generation: '22', actualModel: 'Samsung Galaxy S22 Ultra' },
  '71657tifehl': { brand: 'apple', generation: '15', actualModel: 'Apple iPhone 15' },
  '81+gikwqlil': { brand: 'apple', generation: '15', actualModel: 'Apple iPhone 15 Pro Max' },
  '6175slkkecl': { brand: 'oneplus', generation: 'nord ce 3', actualModel: 'OnePlus Nord CE 3 5G' },
}

/**
 * Validates whether an image URL matches the canonical product identity and generation.
 * Returns true if an image is mismatched or untrusted for that product.
 */
export function isImageMismatch(productName?: string, imageUrl?: string): boolean {
  if (!imageUrl || typeof imageUrl !== 'string') return true
  if (imageUrl === FALLBACK_PRODUCT_IMAGE) return false

  const urlLower = imageUrl.toLowerCase()
  const prodLower = (productName || '').toLowerCase()

  // 1. Check known quarantined signatures
  for (const [sig, meta] of Object.entries(QUARANTINED_IMAGE_SIGNATURES)) {
    if (urlLower.includes(sig)) {
      if (prodLower.includes(meta.brand) && !prodLower.includes(meta.generation)) {
        return true
      }
    }
  }

  // 2. Detect generation mismatch between product name and image URL
  const sMatch = prodLower.match(/\b(?:galaxy\s+)?s(\d{2})\b/)
  if (sMatch) {
    const prodGen = sMatch[1]
    const otherSMatch = urlLower.match(/\bs(\d{2})\b/)
    if (otherSMatch && otherSMatch[1] !== prodGen) {
      return true
    }
  }

  const ipMatch = prodLower.match(/\biphone\s+(\d{1,2})\b/)
  if (ipMatch) {
    const prodGen = ipMatch[1]
    const otherIpMatch = urlLower.match(/\biphone(?:-|\s+)?(\d{1,2})\b/)
    if (otherIpMatch && otherIpMatch[1] !== prodGen) {
      return true
    }
  }

  return false
}

/**
 * Resolves safe image URL for any product card or detail page.
 * Strictly guarantees that no mismatched generation image is ever displayed.
 */
export function resolveSafeProductImage(product?: { name?: string; image?: string; image_url?: string } | null): string {
  if (!product) return FALLBACK_PRODUCT_IMAGE
  const rawUrl = product.image || product.image_url
  if (!rawUrl || typeof rawUrl !== 'string' || rawUrl.trim() === '') {
    return FALLBACK_PRODUCT_IMAGE
  }
  if (isImageMismatch(product.name, rawUrl)) {
    return FALLBACK_PRODUCT_IMAGE
  }
  return rawUrl
}

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


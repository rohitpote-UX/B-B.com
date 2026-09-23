/**
 * Brand Battle — Canonical Currency & Price Formatting Engine
 * Ensures consistent, currency-driven price formatting across all UI components,
 * SEO generators, and data models.
 *
 * Rules:
 * - Indian marketplace listings use INR as canonical currency.
 * - Numerical INR values must NEVER be formatted with '$' unless explicitly converted.
 * - Numerical USD values must NEVER be formatted with '₹'.
 * - Default display currency for Indian marketplace context is INR (₹).
 */

export type CurrencyCode = 'INR' | 'USD' | 'EUR' | 'GBP' | string

export interface FormatPriceOptions {
  currency?: CurrencyCode
  showUSD?: boolean
  showBoth?: boolean
  usdRate?: number
  maximumFractionDigits?: number
}

const DEFAULT_USD_INR_RATE = 84.0

const CURRENCY_SYMBOLS: Record<string, string> = {
  INR: '₹',
  USD: '$',
  EUR: '€',
  GBP: '£',
}

/**
 * Returns the symbol for a given currency code.
 */
export function getCurrencySymbol(currency: CurrencyCode = 'INR'): string {
  return CURRENCY_SYMBOLS[currency.toUpperCase()] || currency
}

/**
 * Formats a canonical INR amount using Indian number grouping (e.g. ₹1,79,900).
 */
export function formatINR(amount: number | null | undefined, maximumFractionDigits?: number): string {
  if (amount == null || isNaN(amount)) return ''
  const num = Number(amount)
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: maximumFractionDigits !== undefined ? maximumFractionDigits : (num % 1 === 0 ? 0 : 2),
  }).format(num)
}

/**
 * Formats a USD amount (e.g. $2,141.67).
 */
export function formatUSD(amount: number | null | undefined, maximumFractionDigits?: number): string {
  if (amount == null || isNaN(amount)) return ''
  const num = Number(amount)
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: maximumFractionDigits !== undefined ? maximumFractionDigits : (num % 1 === 0 ? 0 : 2),
  }).format(num)
}

/**
 * Standardized, currency-driven price formatter.
 *
 * Usage:
 * - formatPrice(179900) -> "₹1,79,900"
 * - formatPrice(179900, "INR") -> "₹1,79,900"
 * - formatPrice(2141.67, "USD") -> "$2,141.67"
 * - formatPrice(179900, "INR", { showBoth: true }) -> "₹1,79,900 ($2,141.67)"
 */
export function formatPrice(
  amount: number | null | undefined,
  currencyOrOptions?: CurrencyCode | FormatPriceOptions,
  maybeOptions?: FormatPriceOptions
): string {
  if (amount == null || isNaN(Number(amount))) return ''
  const num = Number(amount)

  let currency: CurrencyCode = 'INR'
  let options: FormatPriceOptions = {}

  if (typeof currencyOrOptions === 'string') {
    currency = currencyOrOptions
    if (maybeOptions) options = maybeOptions
  } else if (typeof currencyOrOptions === 'object' && currencyOrOptions !== null) {
    options = currencyOrOptions
    currency = options.currency || 'INR'
  }

  const upperCurr = currency.toUpperCase()
  const maxDigits = options.maximumFractionDigits !== undefined
    ? options.maximumFractionDigits
    : (num % 1 === 0 ? 0 : 2)

  let formatted = ''
  if (upperCurr === 'INR') {
    formatted = formatINR(num, maxDigits)
  } else if (upperCurr === 'USD') {
    formatted = formatUSD(num, maxDigits)
  } else {
    try {
      formatted = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: upperCurr,
        maximumFractionDigits: maxDigits,
      }).format(num)
    } catch {
      formatted = `${getCurrencySymbol(upperCurr)}${num.toLocaleString('en-IN')}`
    }
  }

  // If dual-currency display is explicitly requested (e.g. for international buyers)
  if (options.showBoth && upperCurr === 'INR') {
    const rate = options.usdRate || DEFAULT_USD_INR_RATE
    const usdEquivalent = roundToTwoDecimals(num / rate)
    return `${formatted} (${formatUSD(usdEquivalent)})`
  }

  return formatted
}

/**
 * Robust parsing helper to extract numeric price from formatted string.
 * Example: "₹1,79,900" -> 179900
 */
export function parseCurrency(priceStr: string | number | null | undefined): number {
  if (typeof priceStr === 'number') return priceStr
  if (!priceStr) return 0
  const cleaned = String(priceStr).replace(/[^0-9.]/g, '')
  const parsed = parseFloat(cleaned)
  return isNaN(parsed) ? 0 : parsed
}

export function roundToTwoDecimals(val: number): number {
  return Math.round((val + Number.EPSILON) * 100) / 100
}

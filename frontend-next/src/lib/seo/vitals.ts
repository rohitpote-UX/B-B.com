/**
 * Brand Battle — Core Web Vitals Monitoring Integration
 * Reports LCP, INP, CLS, TTFB, and FCP metrics directly to analytics platform.
 */

export interface WebVitalMetric {
  id: string
  name: 'LCP' | 'INP' | 'CLS' | 'TTFB' | 'FCP' | 'FID'
  value: number
  rating: 'good' | 'needs-improvement' | 'poor'
  delta: number
}

/**
 * Handles Web Vitals performance reporting for SEO optimization.
 */
export function reportWebVital(metric: WebVitalMetric): void {
  if (typeof window === 'undefined') return

  // Non-blocking log or send to existing analytics endpoint
  if (process.env.NODE_ENV === 'development') {
    console.log(`[SEO Web Vitals] ${metric.name}: ${metric.value.toFixed(2)} (${metric.rating})`)
  }

  try {
    const body = JSON.stringify({
      metric: metric.name,
      value: metric.value,
      rating: metric.rating,
      page: window.location.pathname,
      timestamp: Date.now(),
    })

    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/analytics/vitals', body)
    }
  } catch {
    // Non-blocking
  }
}

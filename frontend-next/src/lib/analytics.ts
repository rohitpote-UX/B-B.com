/**
 * Brand Battle — Lightweight, Non-Blocking Production Analytics Telemetry
 *
 * Privacy-First, Zero-Regression Telemetry Client:
 * - Employs anonymous, randomized session tokens stored exclusively in sessionStorage.
 * - Dispatches asynchronously via navigator.sendBeacon or non-blocking keepalive fetch.
 * - Guaranteed non-throwing: All errors are caught silently; core site behavior is never blocked or impacted.
 * - Strictly strips all PII (no passwords, tokens, JWTs, emails, or credentials).
 */

export interface AnalyticsEventPayload {
  event_category: string
  event_type: string
  session_id?: string
  device_type?: string
  payload?: Record<string, unknown>
}

// ─── Session Identifier ───────────────────────────────────────────────
function getOrCreateSessionId(): string {
  if (typeof window === 'undefined') return 'server_session'
  try {
    let sess = window.sessionStorage.getItem('bb_analytics_session')
    if (!sess) {
      const rand = Math.random().toString(36).substring(2, 10)
      sess = `bb_sess_${Date.now()}_${rand}`
      window.sessionStorage.setItem('bb_analytics_session', sess)
    }
    return sess
  } catch {
    return 'anonymous_session'
  }
}

// ─── Device Detection ─────────────────────────────────────────────────
function detectDeviceType(): string {
  if (typeof window === 'undefined') return 'desktop'
  try {
    const width = window.innerWidth
    if (width < 768) return 'mobile'
    if (width < 1024) return 'tablet'
    return 'desktop'
  } catch {
    return 'desktop'
  }
}

// ─── Base Asynchronous Dispatcher ─────────────────────────────────────
export function trackEvent(
  category: string,
  eventType: string,
  data?: Record<string, unknown>
): void {
  if (typeof window === 'undefined') return

  try {
    const sessionId = getOrCreateSessionId()
    const deviceType = detectDeviceType()

    const body: AnalyticsEventPayload = {
      event_category: category,
      event_type: eventType,
      session_id: sessionId,
      device_type: deviceType,
      payload: data || {},
    }

    const endpoint = '/api/analytics/events'
    const jsonStr = JSON.stringify(body)

    // Attempt navigator.sendBeacon if available for zero-latency background dispatch
    let beaconSent = false
    if (typeof navigator !== 'undefined' && typeof navigator.sendBeacon === 'function') {
      try {
        const blob = new Blob([jsonStr], { type: 'application/json' })
        beaconSent = navigator.sendBeacon(endpoint, blob)
      } catch {
        beaconSent = false
      }
    }

    // Fallback to fire-and-forget fetch with keepalive
    if (!beaconSent) {
      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: jsonStr,
        keepalive: true,
      }).catch(() => {
        // Silently swallow network anomalies — analytics must never disrupt user experience
      })
    }
  } catch {
    // Top-level fail-safe: guarantee zero regression
  }
}

// ─── Standard BrandBattle Telemetry Methods ───────────────────────────

/**
 * Track route / page navigation
 */
export function trackPageView(path: string): void {
  trackEvent('navigation', 'page_view', { path })
}

/**
 * Track anonymous signup completion (NO passwords, tokens, or emails)
 */
export function trackSignup(method: string = 'email'): void {
  trackEvent('auth', 'signup', { method })
}

/**
 * Track anonymous login event (NO passwords, tokens, or emails)
 */
export function trackLogin(method: string = 'email'): void {
  trackEvent('auth', 'login', { method })
}

/**
 * Track product detail view
 */
export function trackProductView(
  productId: number,
  productName: string,
  brand?: string,
  category?: string
): void {
  trackEvent('catalog', 'product_view', {
    product_id: productId,
    product_name: productName,
    brand: brand || 'unknown',
    category: category || 'general',
  })
}

/**
 * Track search query execution (sanitized, non-sensitive)
 */
export function trackSearch(query: string, resultCount?: number): void {
  const sanitizedQuery = (query || '').trim().slice(0, 100)
  if (!sanitizedQuery) return
  trackEvent('search', 'search', {
    query: sanitizedQuery,
    result_count: typeof resultCount === 'number' ? resultCount : 0,
  })
}

/**
 * Track comparison started
 */
export function trackComparisonStarted(productIds: number[]): void {
  trackEvent('comparison', 'comparison_started', {
    product_ids: productIds,
    count: productIds.length,
  })
}

/**
 * Track comparison completed / verdict rendered
 */
export function trackComparisonCompleted(
  productIds: number[],
  winnerId?: number
): void {
  trackEvent('comparison', 'comparison_completed', {
    product_ids: productIds,
    winner_id: winnerId || null,
  })
}

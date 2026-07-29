import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Protect /profile route
  if (pathname.startsWith('/profile')) {
    const userCookie = request.cookies.get('bb_user')
    
    if (!userCookie) {
      const loginUrl = new URL('/login', request.url)
      return NextResponse.redirect(loginUrl)
    }
  }

  // Redirect authenticated users away from auth pages
  if (pathname === '/login' || pathname === '/signup') {
    const userCookie = request.cookies.get('bb_user')
    
    if (userCookie) {
      const profileUrl = new URL('/profile', request.url)
      return NextResponse.redirect(profileUrl)
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/profile', '/login', '/signup'],
}

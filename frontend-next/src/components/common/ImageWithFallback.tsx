'use client'

import React, { useState } from 'react'
import Image, { ImageProps } from 'next/image'
import { ImageOff } from 'lucide-react'

interface ImageWithFallbackProps extends Omit<ImageProps, 'onError' | 'src'> {
  src?: string | null
  fallbackSrc?: string
  alt: string
}

const DEFAULT_FALLBACK = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400" fill="%2318181b"><rect width="400" height="400" fill="%2318181b"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="14" fill="%2371717a">Product Image Unavailable</text></svg>'

export default function ImageWithFallback({
  src,
  fallbackSrc = DEFAULT_FALLBACK,
  alt,
  className = '',
  ...props
}: ImageWithFallbackProps) {
  const [error, setError] = useState(false)
  const [imgSrc, setImgSrc] = useState<string>(src || fallbackSrc)

  const handleError = () => {
    if (!error) {
      setError(true)
      setImgSrc(fallbackSrc)
    }
  }

  if (!src || error) {
    return (
      <div className={`flex flex-col items-center justify-center bg-theme-subtle rounded-xl text-theme-muted p-4 border border-theme-border/60 ${className}`}>
        <ImageOff className="w-8 h-8 text-[#71717a] mb-1" />
        <span className="text-[0.65rem] uppercase tracking-wider text-[#71717a] font-medium text-center">{alt || 'Image Not Available'}</span>
      </div>
    )
  }

  return (
    <Image
      src={imgSrc}
      alt={alt}
      className={className}
      onError={handleError}
      loading="lazy"
      {...props}
    />
  )
}

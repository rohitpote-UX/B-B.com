'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Building2, Sparkles } from 'lucide-react'
import type { TeamMember } from './page'

function TeamAvatar({
  name,
  initials,
  imageSrc,
}: {
  name: string
  initials: string
  imageSrc: string
}) {
  const [hasError, setHasError] = useState(false)

  return (
    <div className="w-full aspect-square rounded-2xl overflow-hidden bg-gradient-to-br from-[#14141a] via-[#0d0d12] to-[#070709] border border-white/10 relative group-hover:border-[#ff1695]/40 transition-all duration-500 flex items-center justify-center">
      {!hasError ? (
        <img
          src={imageSrc}
          alt={`Photograph of ${name}`}
          onError={() => setHasError(true)}
          className="w-full h-full object-cover object-center filter grayscale contrast-105 group-hover:grayscale-0 transition-all duration-700"
          loading="lazy"
        />
      ) : (
        <div
          className="w-full h-full flex flex-col items-center justify-center p-6 text-center select-none"
          aria-label={`Initials avatar for ${name}`}
        >
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-[#ff1695]/20 to-white/5 border border-[#ff1695]/30 flex items-center justify-center text-[#ff1695] font-mono font-bold text-2xl tracking-widest mb-3 shadow-[0_0_30px_-10px_rgba(255,22,149,0.3)]">
            {initials}
          </div>
          <span className="text-[0.65rem] font-mono uppercase tracking-widest text-white/40">
            Goldspade Executive
          </span>
        </div>
      )}

      {/* Subtle bottom gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#070709] via-transparent to-transparent opacity-60 pointer-events-none" />
    </div>
  )
}

export default function TeamCardList({ members }: { members: TeamMember[] }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
      {members.map((member, idx) => (
        <motion.div
          key={member.name}
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: idx * 0.1 }}
          className="group relative rounded-3xl bg-[#0a0a0d] border border-white/10 hover:border-[#ff1695]/40 p-6 flex flex-col justify-between transition-all duration-500 shadow-xl hover:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.8)]"
        >
          <div>
            {/* Avatar / Photo Container */}
            <div className="mb-6">
              <TeamAvatar
                name={member.name}
                initials={member.initials}
                imageSrc={member.imageSrc}
              />
            </div>

            {/* Role / Company Tag */}
            <div className="flex items-center justify-between gap-2 mb-3">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-[0.7rem] font-mono uppercase tracking-wider text-[#ff1695]">
                <Sparkles className="w-3 h-3" />
                <span>{member.position}</span>
              </span>
              <span className="text-[0.65rem] font-mono uppercase tracking-widest text-white/40">
                {member.company}
              </span>
            </div>

            {/* Member Name */}
            <h2 className="text-xl sm:text-2xl font-bold font-[var(--font-display)] text-white tracking-tight uppercase group-hover:text-[#ff1695] transition-colors mb-2">
              {member.name}
            </h2>

            {/* Factual Bio */}
            {member.bio && (
              <p className="text-xs text-[#8e8e93] leading-relaxed font-light mb-6">
                {member.bio}
              </p>
            )}
          </div>

          {/* Bottom Card Footer */}
          <div className="pt-4 border-t border-white/5 flex items-center justify-between text-[0.7rem] font-mono text-white/50">
            <span className="flex items-center gap-1 text-white/70">
              <Building2 className="w-3 h-3 text-[#ff1695]" />
              <span>{member.company}</span>
            </span>
            <span className="text-white/40">{member.product}</span>
          </div>

          {/* Hover Glow Effect */}
          <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-[#ff1695]/0 via-[#ff1695]/5 to-[#ff1695]/0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
        </motion.div>
      ))}
    </div>
  )
}

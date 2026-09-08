'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { Building2, Crown, Code2, BarChart3, Workflow, Sparkles } from 'lucide-react'
import type { TeamMember } from './page'

function getRoleIcon(position: string) {
  const normalized = position.toLowerCase()
  if (normalized.includes('ceo') || normalized.includes('founder')) {
    return Crown
  }
  if (normalized.includes('cto') || normalized.includes('tech')) {
    return Code2
  }
  if (normalized.includes('cfo') || normalized.includes('financ')) {
    return BarChart3
  }
  if (normalized.includes('coo') || normalized.includes('operat')) {
    return Workflow
  }
  return Sparkles
}

function TeamAvatar({
  name,
  initials,
}: {
  name: string
  initials: string
  imageSrc?: string | null
}) {
  return (
    <div
      className="w-full aspect-square rounded-2xl overflow-hidden bg-gradient-to-br from-[#14141a] via-[#0d0d12] to-[#070709] border border-white/10 relative group-hover:border-[#ff1695]/40 transition-all duration-500 flex flex-col items-center justify-center p-6 text-center select-none"
      aria-label={`Initials avatar for ${name}`}
    >
      {/* Decorative ambient radial glow */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-[#ff1695]/15 via-transparent to-transparent opacity-60 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />

      {/* Large circular initials avatar */}
      <div className="relative z-10 w-24 h-24 sm:w-28 sm:h-28 rounded-full bg-gradient-to-br from-[#181822] via-[#0d0d12] to-[#08080a] border border-white/15 group-hover:border-[#ff1695]/50 flex items-center justify-center shadow-[0_0_35px_-8px_rgba(255,22,149,0.3)] group-hover:shadow-[0_0_50px_-5px_rgba(255,22,149,0.5)] transition-all duration-500">
        <span className="text-2xl sm:text-3xl font-bold font-mono tracking-widest text-white drop-shadow-[0_2px_12px_rgba(0,0,0,0.8)]">
          {initials}
        </span>
      </div>

      <span className="relative z-10 mt-4 text-[0.65rem] font-mono uppercase tracking-[0.2em] text-white/40 group-hover:text-white/70 transition-colors duration-300">
        Goldspade Executive
      </span>

      {/* Subtle bottom gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#070709] via-transparent to-transparent opacity-60 pointer-events-none" />
    </div>
  )
}

export default function TeamCardList({ members }: { members: TeamMember[] }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
      {members.map((member, idx) => {
        const RoleIcon = getRoleIcon(member.position)

        return (
          <motion.div
            key={member.name}
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: idx * 0.1 }}
            className="group relative rounded-3xl bg-[#0a0a0d] border border-white/10 hover:border-[#ff1695]/40 p-6 flex flex-col justify-between transition-all duration-500 shadow-xl hover:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.8)]"
          >
            <div>
              {/* Initials Avatar Container */}
              <div className="mb-6">
                <TeamAvatar
                  name={member.name}
                  initials={member.initials}
                />
              </div>

              {/* Role / Company Tag */}
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-[0.7rem] font-mono uppercase tracking-wider text-[#ff1695]">
                  <RoleIcon className="w-3 h-3" />
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
        )
      })}
    </div>
  )
}

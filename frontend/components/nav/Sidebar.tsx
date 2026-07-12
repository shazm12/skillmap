'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Map, Mic } from 'lucide-react'
import { cn } from '@/lib/utils'

const links = [
  { href: '/roadmap', label: 'Roadmap', icon: Map },
  { href: '/tutor', label: 'Tutor', icon: Mic },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="flex h-screen w-52 shrink-0 flex-col border-r border-border bg-sidebar">
      <div className="px-5 py-6">
        <span className="text-lg font-semibold tracking-tight text-sidebar-foreground">
          SkillMap
        </span>
      </div>

      <nav className="flex flex-col gap-1 px-3">
        {links.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
              pathname === href
                ? 'bg-sidebar-accent text-sidebar-primary'
                : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground'
            )}
          >
            <Icon size={16} />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  )
}

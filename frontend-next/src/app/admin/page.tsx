import type { Metadata } from 'next'
import AdminDashboard from '@/features/admin/AdminDashboard'

export const metadata: Metadata = {
  title: 'Enterprise Command Center | Brand Battle',
  robots: {
    index: false,
    follow: false,
  },
}

export default function AdminPage() {
  return <AdminDashboard />
}

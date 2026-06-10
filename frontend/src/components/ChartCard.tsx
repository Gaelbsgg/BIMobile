import type { ReactNode } from 'react'

export function ChartCard({
  title,
  headerRight,
  children,
  className = '',
}: {
  title: string
  headerRight?: ReactNode
  children: ReactNode
  className?: string
}) {
  return (
    <div className={`rounded-xl border border-outline-variant bg-white p-6 shadow-sm ${className}`}>
      <div className="mb-6 flex items-center justify-between">
        <h4 className="text-headline-md text-primary">{title}</h4>
        {headerRight ? <div className="flex items-center gap-2">{headerRight}</div> : null}
      </div>
      {children}
    </div>
  )
}

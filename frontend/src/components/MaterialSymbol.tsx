export function MaterialSymbol({
  icon,
  className = '',
  filled = false,
}: {
  icon: string
  className?: string
  filled?: boolean
}) {
  return (
    <span
      className={`material-symbols-outlined ${className}`}
      style={filled ? { fontVariationSettings: "'FILL' 1" } : undefined}
      aria-hidden="true"
    >
      {icon}
    </span>
  )
}

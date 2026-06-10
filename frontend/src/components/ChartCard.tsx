import { Area, AreaChart, Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { ChartBlock } from '../types/dashboard'

export function ChartCard({ chart }: { chart: ChartBlock }) {
  const chartProps = {
    data: chart.data,
    margin: { top: 10, right: 0, left: -20, bottom: 0 },
  }

  return (
    <article className="glass rounded-3xl p-5 shadow-glow">
      <h3 className="mb-4 text-lg font-semibold text-white">{chart.title}</h3>
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {chart.type === 'bar' ? (
            <BarChart {...chartProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip />
              <Bar dataKey="value" fill="#E7A83F" radius={[10, 10, 0, 0]} />
            </BarChart>
          ) : chart.type === 'line' ? (
            <LineChart {...chartProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#E7A83F" strokeWidth={3} dot={false} />
            </LineChart>
          ) : (
            <AreaChart {...chartProps}>
              <defs>
                <linearGradient id="fillArea" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#E7A83F" stopOpacity={0.45} />
                  <stop offset="95%" stopColor="#E7A83F" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip />
              <Area type="monotone" dataKey="value" stroke="#E7A83F" fill="url(#fillArea)" strokeWidth={3} />
            </AreaChart>
          )}
        </ResponsiveContainer>
      </div>
    </article>
  )
}

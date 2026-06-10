/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#050816',
          900: '#0B1120',
          800: '#111C33',
        },
        gold: {
          400: '#F4C46D',
          500: '#E7A83F',
        },
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(231, 168, 63, 0.2), 0 20px 80px rgba(0, 0, 0, 0.35)',
      },
    },
  },
  plugins: [],
}

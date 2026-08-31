/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#00D09C', // Mint Green from reference
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
          dark: '#0f172a'
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace']
      },
      boxShadow: {
        'subtle': '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05)',
        'card': '0 4px 20px -2px rgba(15, 23, 42, 0.06)',
        'card-hover': '0 10px 25px -3px rgba(15, 23, 42, 0.1), 0 4px 6px -4px rgba(15, 23, 42, 0.05)',
        'mint': '0 4px 14px 0 rgba(0, 208, 156, 0.35)',
        'mint-hover': '0 6px 20px 0 rgba(0, 208, 156, 0.45)'
      }
    },
  },
  plugins: [],
}

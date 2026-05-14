/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ink: {
          50: '#e8e6df',
          100: '#c9c6bc',
          200: '#9c988c',
          300: '#6f6c63',
          400: '#3d3b36',
          500: '#26241f',
          600: '#1c1a16',
          650: '#181612', // a quiet half-step of elevation
          700: '#141310',
          800: '#0d0c0a',
          900: '#070605',
        },
        parchment: {
          DEFAULT: '#e8e3d3',
          muted: '#b8b2a2',
          dim: '#7a7466',
          shadow: '#56524a',
        },
        accent: {
          DEFAULT: '#b08456', // warmed brass; pulled slightly from the buttery side
          soft: '#82643f',
          deep: '#5a4632',
        },
        rule: '#272520',
        // Muted oxblood — used wherever the editorial register signals
        // trouble (overdue, blocked, reject, errors). Replaces all
        // generic `red-*` references so the palette stays archival.
        signal: {
          DEFAULT: '#a8736a',
          soft: '#825048',
          dim: '#5e423e',
        },
      },
      fontFamily: {
        serif: ['"EB Garamond"', '"Cormorant Garamond"', 'Georgia', 'serif'],
        sans: ['"Inter"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      letterSpacing: {
        wider: '0.08em',
        widest: '0.22em',
      },
      maxWidth: {
        editorial: '78rem',
        chronicle: '34rem', // a book-page width for long-form prose
      },
    },
  },
  plugins: [],
};

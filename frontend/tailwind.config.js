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
          700: '#141310',
          800: '#0d0c0a',
          900: '#070605',
        },
        parchment: {
          DEFAULT: '#e8e3d3',
          muted: '#b8b2a2',
          dim: '#6e6a5e',
        },
        accent: {
          DEFAULT: '#b8915a',
          soft: '#8a6c43',
        },
        rule: '#2a2823',
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
      },
    },
  },
  plugins: [],
};

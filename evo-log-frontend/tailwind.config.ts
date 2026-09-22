import type { Config } from 'tailwindcss'

// Helper  converts a CSS variable name to a Tailwind HSL color reference
const hsl = (varName: string) => `hsl(var(${varName}) / <alpha-value>)`;

const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // ── CSS-variable-based design tokens (Material You / M3-like) ──────────
        background:               hsl('--background'),
        'on-background':          hsl('--on-background'),

        surface:                  hsl('--surface'),
        'on-surface':             hsl('--on-surface'),
        'surface-variant':        hsl('--surface-variant'),
        'on-surface-variant':     hsl('--on-surface-variant'),

        'surface-container-lowest':  hsl('--surface-container-lowest'),
        'surface-container-low':     hsl('--surface-container-low'),
        'surface-container':         hsl('--surface-container'),
        'surface-container-high':    hsl('--surface-container-high'),
        'surface-container-highest': hsl('--surface-container-highest'),

        primary:                  hsl('--primary'),
        'on-primary':             hsl('--on-primary'),
        'primary-container':      hsl('--primary-container'),
        'on-primary-container':   hsl('--on-primary-container'),

        secondary:                hsl('--secondary'),
        'on-secondary':           hsl('--on-secondary'),
        'secondary-container':    hsl('--secondary-container'),
        'on-secondary-container': hsl('--on-secondary-container'),

        tertiary:                 hsl('--tertiary'),
        'on-tertiary':            hsl('--on-tertiary'),
        'tertiary-container':     hsl('--tertiary-container'),
        'on-tertiary-container':  hsl('--on-tertiary-container'),

        error:                    hsl('--error'),
        'on-error':               hsl('--on-error'),
        'error-container':        hsl('--error-container'),
        'on-error-container':     hsl('--on-error-container'),

        outline:                  hsl('--outline'),
        'outline-variant':        hsl('--outline-variant'),

        // ── EVO-LOG brand ────────────────────────────────────────────────────
        'EVO-LOG-primary':        hsl('--EVO-LOG-primary'),

        // ── Legacy / module accent colors ────────────────────────────────────
        'shift-planning':     '#FF6B6B',
        'port-pricing':       '#4ECDC4',
        'gps-tracking':       '#45B7D1',
        'real-customs':       '#96CEB4',
        'port-incidents':     '#FFEAA7',
        'auto-invoicing':     '#DDA0DD',
        'port-performance':   '#98D8C8',
        'notification-system':'#F7DC6F',
        'container-lifecycle':'#BB8FCE',
        'partner-api':        '#85C1E9',

        // ── Gold accent ───────────────────────────────────────────────────────
        gold: {
          50:  '#FFF9E6',
          100: '#FFF3CC',
          200: '#FFE799',
          300: '#FFDB66',
          400: '#FFCF33',
          500: '#FFC300',
          600: '#CC9C00',
          700: '#997500',
          800: '#664E00',
          900: '#332700',
        },
      },

      fontFamily: {
        sans: ['Inter', 'Outfit', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },

      borderRadius: {
        DEFAULT: 'var(--radius)',
      },

      keyframes: {
        shimmer: {
          '0%':   { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition:  '1000px 0' },
        },
      },
      animation: {
        shimmer: 'shimmer 2s infinite linear',
      },
    },
  },
  plugins: [],
}

export default config

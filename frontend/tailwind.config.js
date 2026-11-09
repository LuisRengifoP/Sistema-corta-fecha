/** @type {import('tailwindcss').Config} */

// Tokens de color definidos como variables CSS (triplete RGB) en app.css,
// para soportar modo oscuro via clase .dark y opacidad (bg-x/10).
function tok(nombre) {
  return `rgb(var(--color-${nombre}) / <alpha-value>)`;
}

export default {
  darkMode: 'class',
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        navy: tok('navy'),
        brand: {
          DEFAULT: tok('brand'),
          600: tok('brand'),
          700: tok('brand-700')
        },
        canvas: tok('canvas'),
        surface: tok('surface'),
        ink: tok('ink'),
        muted: tok('muted'),
        line: tok('line'),
        estado: {
          normal: tok('estado-normal'),
          preventiva: tok('estado-preventiva'),
          prioritaria: tok('estado-prioritaria'),
          critica: tok('estado-critica')
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif']
      },
      borderRadius: {
        card: '12px',
        control: '8px'
      },
      boxShadow: {
        card: '0 1px 2px 0 rgba(16, 24, 40, 0.04)',
        elevated: '0 8px 24px -4px rgba(16, 24, 40, 0.12)'
      },
      fontSize: {
        kpi: ['28px', { lineHeight: '32px', fontWeight: '700' }]
      }
    }
  },
  plugins: []
};

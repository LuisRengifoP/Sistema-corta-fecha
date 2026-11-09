/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        navy: '#172B4D',
        brand: {
          DEFAULT: '#2563EB',
          600: '#2563EB',
          700: '#1D4ED8'
        },
        canvas: '#F4F6F9',
        surface: '#FFFFFF',
        ink: '#263445',
        muted: '#64748B',
        line: '#E2E8F0',
        estado: {
          normal: '#16A34A',
          preventiva: '#EAB308',
          prioritaria: '#F97316',
          critica: '#DC2626'
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

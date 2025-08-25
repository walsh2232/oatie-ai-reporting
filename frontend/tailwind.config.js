/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        redwood: {
          brand: {
            1: '#312D2A',
            2: '#522916',
            3: '#A76914',
            4: '#ED6C02',
            5: '#FFB000',
          },
          neutral: {
            0: '#FFFFFF',
            10: '#FAFAFA',
            20: '#F5F5F5',
            30: '#EBEBEB',
            40: '#D6D6D6',
            50: '#CCCCCC',
            60: '#999999',
            70: '#666666',
            80: '#333333',
            90: '#1A1A1A',
          },
          success: '#0F7B0F',
          warning: '#FF8800',
          danger: '#C74634',
          info: '#0572CE',
        }
      },
      fontFamily: {
        'redwood': ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      }
    },
  },
  plugins: [],
}
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))"
      },
      colors: {
        'liquid-accent':'#14C5BB',
        'bg-white': '#FCFFFF',
        'liquid-text': '#273A3A',
        'liquid-primary': '#00B1AB',
        'bg-liquid-blur': 'rgba(20, 197, 187, 0.2)'
      },
      dropShadow: {
        'md': '0 0 7px rgba(20, 197, 187, 0.2)'
      },
      keyframes: {
        slideLeft: {
          '0%': { 
            transform: 'translateX(-100%)'
          },
          '100%': {
            transform: 'translateX(0%)'
          }
        }
      },
      animation: {
        slideLeft: 'slideLeft 0.5s ease-in-out'
      }
    },
  },
  plugins: [],
};

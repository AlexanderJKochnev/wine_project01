/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: ["light", "dark", "cupcake"],
  },
  safelist: [
    'btn',
    'btn-primary',
    'input',
    'input-bordered',
    'card',
    'form-control',
    'alert',
    'alert-error',
    'text-center',
    'w-full',
    'max-w-md',
    'p-6',
    'shadow-lg',
    'bg-base-100',
    'min-h-screen',
    'flex',
    'items-center',
    'justify-center',
    'p-4',
    'flex',
    'flex-col',
    'container',
    'mx-auto',
    'p-4',
    'flex-grow',
    'space-y-4',
    'text-2xl',
    'font-bold',
    'mb-4',
    'mt-4',
  ]
}
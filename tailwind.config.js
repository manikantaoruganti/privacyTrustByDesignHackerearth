// // // /** @type {import('tailwindcss').Config} */
// // // export default {
// // //   content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
// // //   theme: {
// // //     extend: {},
// // //   },
// // //   plugins: [],
// // // };
// // /** @type {import('tailwindcss').Config} */
// // export default {
// //   content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
// //   theme: {
// //     extend: {
// //       colors: {
// //         success: {
// //           50: '#f0fdf4',
// //           100: '#dcfce7',
// //           200: '#bbf7d0',
// //           300: '#86efac',
// //           400: '#4ade80',
// //           500: '#22c55e',
// //           600: '#16a34a',
// //           700: '#15803d',  // ✅ hover:bg-success-700 will now work
// //           800: '#166534',
// //           900: '#14532d',
// //         },
// //         warning: {
// //           500: '#f59e0b',
// //           700: '#b45309',
// //         },
// //         danger: {
// //           500: '#ef4444',
// //           700: '#b91c1c',
// //         },
// //         info: {
// //           500: '#3b82f6',
// //           700: '#1d4ed8',
// //         },
// //       },
// //     },
// //   },
// //   plugins: [],
// // };
// /** @type {import('tailwindcss').Config} */
// export default {
//   content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
//   theme: {
//     extend: {
//       colors: {
//         success: {
//           700: '#15803d', // dark green, you can choose any hex
//         },
//       },
//     },
//   },
//   plugins: [],
// };
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e', // base
          600: '#16a34a',
          700: '#15803d', // dark
          800: '#166534',
          900: '#14532d',
        },
      },
    },
  },
  plugins: [],
};

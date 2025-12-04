/**
 * PostCSS Configuration
 *
 * PostCSS is a tool that processes CSS files. Think of it as a translator
 * that transforms modern CSS into CSS that works in all browsers.
 *
 * Plugins enabled:
 * - tailwindcss: Processes Tailwind's utility classes (like 'bg-blue-500')
 *   and generates the actual CSS
 * - autoprefixer: Automatically adds browser prefixes (like -webkit-, -moz-)
 *   to CSS properties so they work in older browsers
 *
 * This file is automatically used by Vite during the build process.
 * You rarely need to modify this.
 */

export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

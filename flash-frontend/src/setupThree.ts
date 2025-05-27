/**
 * Three.js configuration to suppress deprecation warnings
 */

// Suppress Three.js warnings in development
if (process.env.NODE_ENV === 'development') {
  const originalWarn = console.warn;
  console.warn = (...args) => {
    // Filter out Three.js deprecation warnings
    if (
      args[0]?.includes?.('THREE.') && 
      (args[0].includes('deprecated') || 
       args[0].includes('will be removed') ||
       args[0].includes('has been renamed'))
    ) {
      return;
    }
    originalWarn.apply(console, args);
  };
}

export {};
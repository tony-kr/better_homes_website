// Shared handle to the app's single Lenis instance, so overlays can
// pause the page scroll without prop-drilling through every section.
let lenis = null;

export const setLenis = (instance) => {
  lenis = instance;
};

export const getLenis = () => lenis;

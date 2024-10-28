

const local = "http://localhost:2357/backend";
const production = "http://144.34.219.61:2357/backend";
export const isProduction = !import.meta.env.DEV;
export const serverURL = isProduction ? production : local;

export const DEBUG_MODE = true;
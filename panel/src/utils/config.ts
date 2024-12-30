

const localLocalhost = "http://localhost:2359/backend";
const localServer = "http://10.100.5.91:2359/backend";
const local = localLocalhost;
const production = "http://144.34.219.61:2357/backend";
export const isProduction = !import.meta.env.DEV;
export const serverURL = isProduction ? production : local;

export const DEBUG_MODE = true;
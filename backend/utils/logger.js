export const logger = {
  info: (msg) => console.log(`[INFO] ${new Date().toISOString()}: ${msg}`),
  error: (msg) => console.error(`[ERROR] ${new Date().toISOString()}: ${msg}`),
  warn: (msg) => console.warn(`[WARN] ${new Date().toISOString()}: ${msg}`),
};

export const requestLogger = (req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(
      `[HTTP] ${new Date().toISOString()} - ${req.method} ${req.originalUrl} - ` +
      `Status: ${res.statusCode} - Duration: ${duration}ms - IP: ${req.ip}`
    );
  });
  next();
};

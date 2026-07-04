import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { connectDB } from './config/database.js';
import { requestLogger, logger } from './utils/logger.js';
import trafficRoutes from './routes/trafficRoutes.js';
import signalRoutes from './routes/signalRoutes.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/smart_traffic';

// Express Middleware
app.use(cors());
app.use(express.json());
app.use(requestLogger);

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'smart-traffic-backend-service',
    timestamp: new Date().toISOString(),
  });
});

// REST API Route mapping
app.use('/api/traffic', trafficRoutes);
app.use('/api/signals', signalRoutes);

// Global error handling middleware
app.use((err, req, res, next) => {
  logger.error(`Unhandled error: ${err.message}\nStack: ${err.stack}`);
  res.status(err.status || 500).json({
    error: err.message || 'Internal Server Error',
  });
});

// Database connection and server initialization
connectDB(MONGODB_URI)
  .then(() => {
    app.listen(PORT, () => {
      logger.info(`REST API Server is running on port ${PORT}`);
    });
  })
  .catch((err) => {
    logger.error(`Server initialization failed: ${err.message}`);
    process.exit(1);
  });

export default app;

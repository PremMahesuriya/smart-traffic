import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { connectDB } from './config/db.js';
import trafficRoutes from './routes/traffic.js';
import cameraRoutes from './routes/cameras.js';
import accidentRoutes from './routes/accidents.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', service: 'smart-traffic-api' });
});

app.use('/api', trafficRoutes);
app.use('/api/cameras', cameraRoutes);
app.use('/api/accidents', accidentRoutes);

connectDB(process.env.MONGODB_URI || 'mongodb://localhost:27017/smart_traffic').then(() => {
  app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
});

export default app;

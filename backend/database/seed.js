import mongoose from 'mongoose';
import dotenv from 'dotenv';
import Camera from '../src/models/Camera.js';
import Signal from '../src/models/Signal.js';
import TrafficLog from '../src/models/TrafficLog.js';

dotenv.config();

const INTERSECTION = 'INT-001';

async function seed() {
  const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017/smart_traffic';
  await mongoose.connect(uri);

  await Promise.all([
    Camera.deleteMany({}),
    Signal.deleteMany({}),
    TrafficLog.deleteMany({}),
  ]);

  await Camera.create([
    { name: 'Cam North', location: 'Lane A/B approach', status: 'online', intersectionId: INTERSECTION },
    { name: 'Cam South', location: 'Lane C/D approach', status: 'online', intersectionId: INTERSECTION },
  ]);

  const laneData = [
    { lane: 'A', vehicleCount: 50, density: 'High', greenDurationSec: 60 },
    { lane: 'B', vehicleCount: 8, density: 'Low', greenDurationSec: 15 },
    { lane: 'C', vehicleCount: 15, density: 'Medium', greenDurationSec: 35 },
    { lane: 'D', vehicleCount: 40, density: 'Very High', greenDurationSec: 55 },
  ];

  await Signal.insertMany(
    laneData.map((d) => ({
      intersectionId: INTERSECTION,
      state: 'red',
      ...d,
    }))
  );

  await TrafficLog.insertMany(
    laneData.map((d) => ({
      intersectionId: INTERSECTION,
      lane: d.lane,
      vehicleCount: d.vehicleCount,
      density: d.density,
      avgWaitTimeSec: d.greenDurationSec * 0.4,
      congestionPercent: d.vehicleCount,
    }))
  );

  console.log('Database seeded successfully');
  await mongoose.disconnect();
}

seed().catch((err) => {
  console.error(err);
  process.exit(1);
});

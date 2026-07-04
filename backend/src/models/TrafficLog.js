import mongoose from 'mongoose';

const trafficLogSchema = new mongoose.Schema(
  {
    intersectionId: String,
    lane: String,
    vehicleCount: Number,
    density: String,
    avgWaitTimeSec: Number,
    congestionPercent: Number,
    recordedAt: { type: Date, default: Date.now },
  },
  { timestamps: true }
);

export default mongoose.model('TrafficLog', trafficLogSchema);

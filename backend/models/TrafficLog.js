import mongoose from 'mongoose';

const trafficLogSchema = new mongoose.Schema(
  {
    timestamp: {
      type: Number, // Stores elapsed time from video frame start or epoch
      required: true,
    },
    lane: {
      type: String, // 'A', 'B', 'C', 'D'
      required: true,
      enum: ['A', 'B', 'C', 'D'],
    },
    vehicleCount: {
      type: Number,
      required: true,
      min: 0,
    },
    density: {
      type: String, // 'Low', 'Medium', 'High', 'Very High'
      required: true,
      enum: ['Low', 'Medium', 'High', 'Very High'],
    },
    processingTime: {
      type: Number, // in milliseconds
      default: 0,
    },
  },
  {
    timestamps: true, // Auto-adds createdAt and updatedAt
  }
);

// Indexing for faster history queries and analytics aggregation
trafficLogSchema.index({ lane: 1, timestamp: -1 });

export default mongoose.model('TrafficLog', trafficLogSchema);

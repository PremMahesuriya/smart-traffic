import mongoose from 'mongoose';

const signalLogSchema = new mongoose.Schema(
  {
    timestamp: {
      type: Number,
      required: true,
    },
    activeLane: {
      type: String, // 'A', 'B', 'C', 'D' or 'None'
      required: true,
    },
    signalState: {
      type: String, // 'GREEN', 'YELLOW', 'RED'
      required: true,
      enum: ['GREEN', 'YELLOW', 'RED', 'none'],
    },
    greenTime: {
      type: Number,
      required: true,
      min: 0,
    },
    remainingTime: {
      type: Number,
      required: true,
      min: 0,
    },
  },
  {
    timestamps: true,
  }
);

signalLogSchema.index({ activeLane: 1, timestamp: -1 });

export default mongoose.model('SignalLog', signalLogSchema);

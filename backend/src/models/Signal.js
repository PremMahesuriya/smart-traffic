import mongoose from 'mongoose';

const signalSchema = new mongoose.Schema(
  {
    intersectionId: { type: String, required: true },
    lane: { type: String, required: true },
    state: { type: String, enum: ['red', 'yellow', 'green'], default: 'red' },
    greenDurationSec: { type: Number, default: 30 },
    vehicleCount: { type: Number, default: 0 },
    density: { type: String, enum: ['Low', 'Medium', 'High', 'Very High'] },
  },
  { timestamps: true }
);

export default mongoose.model('Signal', signalSchema);

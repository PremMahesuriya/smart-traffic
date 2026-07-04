import mongoose from 'mongoose';

const vehicleSchema = new mongoose.Schema(
  {
    cameraId: { type: mongoose.Schema.Types.ObjectId, ref: 'Camera' },
    class: { type: String, enum: ['car', 'bus', 'truck', 'bike'] },
    lane: String,
    count: { type: Number, default: 1 },
    timestamp: { type: Date, default: Date.now },
  },
  { timestamps: true }
);

export default mongoose.model('Vehicle', vehicleSchema);

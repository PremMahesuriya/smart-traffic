import mongoose from 'mongoose';

const cameraSchema = new mongoose.Schema(
  {
    name: { type: String, required: true },
    location: { type: String, required: true },
    streamUrl: String,
    status: { type: String, enum: ['online', 'offline'], default: 'offline' },
    intersectionId: String,
  },
  { timestamps: true }
);

export default mongoose.model('Camera', cameraSchema);

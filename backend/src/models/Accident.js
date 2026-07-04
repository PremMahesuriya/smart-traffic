import mongoose from 'mongoose';

const accidentSchema = new mongoose.Schema(
  {
    cameraId: { type: mongoose.Schema.Types.ObjectId, ref: 'Camera' },
    type: { type: String, enum: ['collision', 'sudden_stop', 'road_block', 'smoke'] },
    location: String,
    status: { type: String, enum: ['active', 'resolved'], default: 'active' },
    alertSent: { type: Boolean, default: false },
  },
  { timestamps: true }
);

export default mongoose.model('Accident', accidentSchema);

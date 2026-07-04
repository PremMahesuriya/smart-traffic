import express from 'express';
import Signal from '../models/Signal.js';
import TrafficLog from '../models/TrafficLog.js';
import Vehicle from '../models/Vehicle.js';

const router = express.Router();

router.get('/traffic', async (_req, res) => {
  try {
    const logs = await TrafficLog.find().sort({ recordedAt: -1 }).limit(50);
    const latestByLane = await TrafficLog.aggregate([
      { $sort: { recordedAt: -1 } },
      { $group: { _id: '$lane', doc: { $first: '$$ROOT' } } },
    ]);
    res.json({ logs, latestByLane: latestByLane.map((l) => l.doc) });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get('/camera', async (_req, res) => {
  res.redirect(307, '/api/cameras');
});

router.get('/signals', async (_req, res) => {
  try {
    const signals = await Signal.find().sort({ lane: 1 });
    res.json(signals);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post('/signal', async (req, res) => {
  try {
    const { intersectionId, lane, greenDurationSec, vehicleCount, density, state } = req.body;
    const signal = await Signal.findOneAndUpdate(
      { intersectionId, lane },
      { greenDurationSec, vehicleCount, density, state },
      { upsert: true, new: true }
    );
    res.json(signal);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get('/analytics', async (_req, res) => {
  try {
    const [totalVehicles, recentAccidents, signals] = await Promise.all([
      Vehicle.countDocuments(),
      TrafficLog.aggregate([
        {
          $group: {
            _id: { $hour: '$recordedAt' },
            count: { $sum: '$vehicleCount' },
          },
        },
        { $sort: { _id: 1 } },
      ]),
      Signal.find(),
    ]);

    const avgWait =
      signals.length > 0
        ? signals.reduce((s, sig) => s + (sig.greenDurationSec || 0), 0) / signals.length
        : 0;

    res.json({
      totalVehicles,
      hourlyTraffic: recentAccidents,
      averageWaitTimeSec: Math.round(avgWait),
      signals,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;

import TrafficLog from '../models/TrafficLog.js';
import SignalLog from '../models/SignalLog.js';

// POST /api/internal/updateTraffic
export const updateTraffic = async (req, res, next) => {
  try {
    const { timestamp, laneCounts, densities, signal, metrics } = req.body;

    if (timestamp === undefined) {
      return res.status(400).json({ error: 'Missing timestamp' });
    }

    // 1. Bulk insert TrafficLog for lanes A, B, C, D
    const trafficLogs = [];
    const lanes = ['A', 'B', 'C', 'D'];

    lanes.forEach((lane) => {
      const vehicleCount = laneCounts ? laneCounts[lane] || 0 : 0;
      const density = densities ? densities[lane] || 'Low' : 'Low';
      const processingTime = metrics ? metrics.latency || 0 : 0;

      trafficLogs.push({
        timestamp,
        lane,
        vehicleCount,
        density,
        processingTime,
      });
    });

    await TrafficLog.insertMany(trafficLogs);

    // 2. Insert SignalLog if signal update is provided
    if (signal) {
      await SignalLog.create({
        timestamp,
        activeLane: signal.activeLane || 'None',
        signalState: (signal.signalState || 'RED').toUpperCase(),
        greenTime: signal.greenTime || 0,
        remainingTime: signal.remainingTime || 0,
      });
    }

    res.status(200).json({
      message: 'System state updated successfully',
      timestamp,
    });
  } catch (error) {
    next(error);
  }
};

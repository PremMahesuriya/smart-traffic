import SignalLog from '../models/SignalLog.js';

// GET /api/signals/current
export const getCurrentSignal = async (req, res, next) => {
  try {
    const latest = await SignalLog.findOne().sort({ timestamp: -1 });

    if (!latest) {
      return res.json({
        activeLane: 'None',
        signal: 'RED',
        remainingTime: 0,
      });
    }

    res.json({
      activeLane: latest.activeLane,
      signal: latest.signalState,
      remainingTime: Math.round(latest.remainingTime),
    });
  } catch (error) {
    next(error);
  }
};

// GET /api/signals/history
export const getSignalHistory = async (req, res, next) => {
  try {
    const history = await SignalLog.find().sort({ timestamp: -1 }).limit(100);
    res.json(history);
  } catch (error) {
    next(error);
  }
};

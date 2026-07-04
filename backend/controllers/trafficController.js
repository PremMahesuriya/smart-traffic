import TrafficLog from '../models/TrafficLog.js';

// GET /api/traffic/current
export const getCurrentTraffic = async (req, res, next) => {
  try {
    // Group by lane and get the latest document sorted by timestamp
    const latestLogs = await TrafficLog.aggregate([
      { $sort: { timestamp: -1 } },
      {
        $group: {
          _id: '$lane',
          doc: { $first: '$$ROOT' },
        },
      },
    ]);

    const result = {
      laneA: { count: 0, density: 'Low' },
      laneB: { count: 0, density: 'Low' },
      laneC: { count: 0, density: 'Low' },
      laneD: { count: 0, density: 'Low' },
    };

    latestLogs.forEach((item) => {
      const laneKey = `lane${item._id}`;
      if (laneKey in result) {
        result[laneKey] = {
          count: item.doc.vehicleCount,
          density: item.doc.density,
        };
      }
    });

    res.json(result);
  } catch (error) {
    next(error);
  }
};

// GET /api/traffic/history
export const getTrafficHistory = async (req, res, next) => {
  try {
    const history = await TrafficLog.find()
      .sort({ timestamp: -1, lane: 1 })
      .limit(100);
    res.json(history);
  } catch (error) {
    next(error);
  }
};

// GET /api/traffic/analytics
export const getTrafficAnalytics = async (req, res, next) => {
  try {
    // Run aggregation to calculate averages and max counts per lane
    const laneStats = await TrafficLog.aggregate([
      {
        $group: {
          _id: '$lane',
          avgCount: { $avg: '$vehicleCount' },
          maxCount: { $max: '$vehicleCount' },
        },
      },
    ]);

    if (laneStats.length === 0) {
      return res.json({
        totalVehicles: 0,
        averageVehiclesPerLane: 0,
        busiestLane: 'None',
        leastBusyLane: 'None',
      });
    }

    // Calculate total vehicles across all logs
    // (As a metric, we sum the peak/max count detected in each lane)
    let totalVehicles = 0;
    let busiestLane = 'None';
    let busiestCount = -1;
    let leastBusyLane = 'None';
    let leastBusyCount = Infinity;
    let totalAvgSum = 0;

    laneStats.forEach((stat) => {
      totalVehicles += stat.maxCount;
      totalAvgSum += stat.avgCount;

      if (stat.avgCount > busiestCount) {
        busiestCount = stat.avgCount;
        busiestLane = stat._id;
      }
      if (stat.avgCount < leastBusyCount) {
        leastBusyCount = stat.avgCount;
        leastBusyLane = stat._id;
      }
    });

    const avgVehiclesPerLane = Math.round((totalAvgSum / laneStats.length) * 100) / 100;

    res.json({
      totalVehicles,
      averageVehiclesPerLane: avgVehiclesPerLane,
      busiestLane: `Lane ${busiestLane}`,
      leastBusyLane: `Lane ${leastBusyLane}`,
    });
  } catch (error) {
    next(error);
  }
};

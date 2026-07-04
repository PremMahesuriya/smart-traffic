import express from 'express';
import {
  getCurrentTraffic,
  getTrafficHistory,
  getTrafficAnalytics,
} from '../controllers/trafficController.js';

const router = express.Router();

router.get('/current', getCurrentTraffic);
router.get('/history', getTrafficHistory);
router.get('/analytics', getTrafficAnalytics);

export default router;

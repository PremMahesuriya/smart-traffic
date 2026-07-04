import express from 'express';
import { getCurrentSignal, getSignalHistory } from '../controllers/signalController.js';

const router = express.Router();

router.get('/current', getCurrentSignal);
router.get('/history', getSignalHistory);

export default router;

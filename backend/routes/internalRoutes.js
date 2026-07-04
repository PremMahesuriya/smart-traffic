import express from 'express';
import { updateTraffic } from '../controllers/internalController.js';

const router = express.Router();

router.post('/updateTraffic', updateTraffic);

export default router;

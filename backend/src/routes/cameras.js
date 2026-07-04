import express from 'express';
import Camera from '../models/Camera.js';

const router = express.Router();

router.get('/', async (_req, res) => {
  try {
    const cameras = await Camera.find();
    res.json(cameras);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post('/', async (req, res) => {
  try {
    const camera = await Camera.create(req.body);
    res.status(201).json(camera);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

export default router;

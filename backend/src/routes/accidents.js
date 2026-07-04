import express from 'express';
import Accident from '../models/Accident.js';

const router = express.Router();

router.get('/', async (_req, res) => {
  try {
    const accidents = await Accident.find().sort({ createdAt: -1 });
    res.json(accidents);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post('/', async (req, res) => {
  try {
    const accident = await Accident.create(req.body);
    res.status(201).json(accident);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

export default router;

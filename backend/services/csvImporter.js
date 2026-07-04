import fs from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import { connectDB } from '../config/database.js';
import TrafficLog from '../models/TrafficLog.js';
import SignalLog from '../models/SignalLog.js';

dotenv.config();

const __dirname = dirname(fileURLToPath(import.meta.url));
const outputDir = join(__dirname, '../../output');

// Simple CSV parser helper
const parseCSV = (filePath) => {
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n').map((line) => line.trim()).filter((line) => line.length > 0);
  if (lines.length === 0) return [];

  const headers = lines[0].split(',').map((h) => h.trim());
  return lines.slice(1).map((line) => {
    const values = line.split(',').map((v) => v.trim());
    const obj = {};
    headers.forEach((h, i) => {
      obj[h] = values[i] || '';
    });
    return obj;
  });
};

// Map count to density based on Phase 4 config
const getDensity = (count) => {
  if (count <= 5) return 'Low';
  if (count <= 10) return 'Medium';
  if (count <= 20) return 'High';
  return 'Very High';
};

export const importCSVData = async () => {
  console.log(`[IMPORTER] Scanning output directory for CSV logs in: ${outputDir}`);

  if (!fs.existsSync(outputDir)) {
    console.warn(`[IMPORTER] Output directory not found. No CSVs to import.`);
    return;
  }

  const files = fs.readdirSync(outputDir);
  const laneCountsFiles = files.filter((f) => f.endsWith('_lane_counts.csv'));
  const signalLogsFiles = files.filter((f) => f.endsWith('_signal_logs.csv'));

  console.log(`[IMPORTER] Found ${laneCountsFiles.length} lane count CSV files.`);
  console.log(`[IMPORTER] Found ${signalLogsFiles.length} signal log CSV files.`);

  // Clear existing databases to start fresh
  await Promise.all([
    TrafficLog.deleteMany({}),
    SignalLog.deleteMany({}),
  ]);
  console.log('[IMPORTER] Cleared existing TrafficLogs and SignalLogs databases.');

  // Import Traffic Logs
  for (const file of laneCountsFiles) {
    const filePath = join(outputDir, file);
    try {
      console.log(`[IMPORTER] Processing: ${file}`);
      const rows = parseCSV(filePath);
      const logsToInsert = [];

      rows.forEach((row) => {
        const timestamp = parseFloat(row['Timestamp']);
        if (isNaN(timestamp)) return;

        // Process for each lane A, B, C, D
        ['A', 'B', 'C', 'D'].forEach((lane) => {
          const liveCountKey = `Lane_${lane}_Live`;
          const count = parseInt(row[liveCountKey], 10) || 0;

          logsToInsert.push({
            timestamp,
            lane,
            vehicleCount: count,
            density: getDensity(count),
            processingTime: 60.0, // Benchmark average from Phase 4
          });
        });
      });

      if (logsToInsert.length > 0) {
        await TrafficLog.insertMany(logsToInsert);
        console.log(`[IMPORTER] Successfully imported ${logsToInsert.length} traffic log records from ${file}`);
      }
    } catch (err) {
      console.error(`[IMPORTER] Error importing ${file}: ${err.message}`);
    }
  }

  // Import Signal Logs
  for (const file of signalLogsFiles) {
    const filePath = join(outputDir, file);
    try {
      console.log(`[IMPORTER] Processing: ${file}`);
      const rows = parseCSV(filePath);
      const logsToInsert = [];

      rows.forEach((row) => {
        const timestamp = parseFloat(row['Timestamp']);
        if (isNaN(timestamp)) return;

        const activeLane = row['Lane'] || 'None';
        const signalState = (row['Signal Status'] || 'RED').toUpperCase();
        const greenTime = parseInt(row['Assigned Green Time'], 10) || 0;

        logsToInsert.push({
          timestamp,
          activeLane,
          signalState,
          greenTime,
          remainingTime: greenTime, // Default countdown
        });
      });

      if (logsToInsert.length > 0) {
        await SignalLog.insertMany(logsToInsert);
        console.log(`[IMPORTER] Successfully imported ${logsToInsert.length} signal logs from ${file}`);
      }
    } catch (err) {
      console.error(`[IMPORTER] Error importing ${file}: ${err.message}`);
    }
  }

  console.log('[IMPORTER] Data import completed successfully.');
};

// Run script directly if executed from command line
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017/smart_traffic';
  connectDB(uri)
    .then(() => importCSVData())
    .then(() => {
      console.log('[IMPORTER] Script execution finished.');
      process.exit(0);
    })
    .catch((err) => {
      console.error('[IMPORTER] Script failed:', err);
      process.exit(1);
    });
}

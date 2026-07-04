# MongoDB Collections — Phase 10

| Collection     | Fields |
|----------------|--------|
| **users**      | name, email, password (hashed), role (admin/operator) |
| **cameras**    | name, location, streamUrl, status, intersectionId |
| **vehicles**   | cameraId, class, lane, count, timestamp |
| **signals**    | intersectionId, lane, state, greenDurationSec, vehicleCount, density |
| **traffic_logs** | intersectionId, lane, vehicleCount, density, avgWaitTimeSec, congestionPercent, recordedAt |
| **accidents**  | cameraId, type, location, status, alertSent |
| **analytics**  | Aggregated via API from traffic_logs and vehicles |

Run seed script:

```bash
cd backend && npm run seed
```

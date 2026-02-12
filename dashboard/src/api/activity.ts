/**
 * Industrial Wearable AI — Activity timeline API
 */
import { apiClient } from "./client";

export interface TimelineBucket {
  minute: string;
  sewing: number;
  adjusting: number;
  idle: number;
  break: number;
  error: number;
}

export async function getActivityTimeline(
  fromTs: number,
  toTs: number,
  bucketMinutes: number = 1
): Promise<TimelineBucket[]> {
  const { data } = await apiClient.get<TimelineBucket[]>("/api/activity/timeline", {
    params: { from_ts: fromTs, to_ts: toTs, bucket_minutes: bucketMinutes },
  });
  return data;
}

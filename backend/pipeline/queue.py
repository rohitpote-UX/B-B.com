"""
Brand Battle - Pipeline Queue & Dead-Letter Queue (DLQ) Engine
Provides non-blocking stream processing via Redis Streams with fallback memory queues.
"""

import json
import time
from typing import List, Dict, Any, Optional
from redis_client import redis_client, is_redis_healthy
import logging

logger = logging.getLogger("brandbattle.queue")

STREAM_RAW = "pipeline:raw_stream"
STREAM_VALIDATED = "pipeline:validated_stream"
KEY_DLQ = "pipeline:dlq"


class PipelineQueueManager:
    """Manages stream message publishing, batch popping, and Dead-Letter Queueing."""

    def __init__(self):
        self._memory_raw_queue: List[Dict[str, Any]] = []
        self._memory_dlq: List[Dict[str, Any]] = []

    def publish_raw(self, item: Dict[str, Any]) -> bool:
        """Pushes raw scraped item payload into the ingestion queue stream."""
        payload_str = json.dumps(item, default=str)
        if is_redis_healthy():
            try:
                redis_client.xadd(STREAM_RAW, {"data": payload_str})
                return True
            except Exception as e:
                logger.error(f"Failed to publish to Redis Stream: {e}")
        
        # Memory queue fallback
        self._memory_raw_queue.append(item)
        return True

    def pop_raw_batch(self, count: int = 20) -> List[Dict[str, Any]]:
        """Reads a batch of raw scraped payloads from the queue."""
        results: List[Dict[str, Any]] = []
        
        if is_redis_healthy():
            try:
                # Read from Redis stream using XREAD
                entries = redis_client.xread({STREAM_RAW: "0-0"}, count=count)
                if entries:
                    for stream_name, messages in entries:
                        for msg_id, fields in messages:
                            if "data" in fields:
                                item = json.loads(fields["data"])
                                results.append(item)
                                # Delete message after reading to simulate queue popping
                                redis_client.xdel(STREAM_RAW, msg_id)
                    return results
            except Exception as e:
                logger.error(f"Failed to pop batch from Redis Stream: {e}")

        # Pop from memory queue fallback
        for _ in range(min(count, len(self._memory_raw_queue))):
            results.append(self._memory_raw_queue.pop(0))
            
        return results

    def push_dlq(self, item: Dict[str, Any], reason: str) -> bool:
        """Sends corrupted or unprocessable records to Dead-Letter Queue with failure diagnostic reason."""
        dlq_entry = {
            "item": item,
            "reason": reason,
            "failed_at": time.time()
        }
        dlq_str = json.dumps(dlq_entry, default=str)

        if is_redis_healthy():
            try:
                redis_client.lpush(KEY_DLQ, dlq_str)
                # Keep last 1000 DLQ items
                redis_client.ltrim(KEY_DLQ, 0, 999)
                return True
            except Exception as e:
                logger.error(f"Failed to push to Redis DLQ: {e}")

        self._memory_dlq.insert(0, dlq_entry)
        if len(self._memory_dlq) > 1000:
            self._memory_dlq.pop()
        return True

    def get_dlq_records(self, count: int = 50) -> List[Dict[str, Any]]:
        """Fetch dead-letter queue records for pipeline monitoring and auditing."""
        if is_redis_healthy():
            try:
                raw_list = redis_client.lrange(KEY_DLQ, 0, count - 1)
                return [json.loads(x) for x in raw_list]
            except Exception as e:
                logger.error(f"Failed to fetch DLQ records from Redis: {e}")

        return self._memory_dlq[:count]

    def get_queue_depth(self) -> Dict[str, int]:
        """Returns pending queue length and DLQ metrics."""
        raw_depth = 0
        dlq_depth = 0

        if is_redis_healthy():
            try:
                raw_depth = redis_client.xlen(STREAM_RAW)
                dlq_depth = redis_client.llen(KEY_DLQ)
            except Exception:
                pass
        else:
            raw_depth = len(self._memory_raw_queue)
            dlq_depth = len(self._memory_dlq)

        return {
            "raw_queue_depth": raw_depth,
            "dlq_depth": dlq_depth
        }


# Global queue manager instance
queue_manager = PipelineQueueManager()

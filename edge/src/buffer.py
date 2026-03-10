"""
Industrial Wearable AI — Sample Buffer
Ring buffer for raw IMU samples. Used by pipeline for sliding windows.
"""
from collections import deque
from typing import Any, List, Optional


class SampleBuffer:
    """
    Ring buffer for samples. maxlen = max_seconds * sample_rate.
    Thread-safe for single-threaded async usage.
    """

    def __init__(self, max_seconds: float = 5.0, sample_rate: float = 25.0):
        self.max_seconds = max_seconds
        self.sample_rate = sample_rate
        maxlen = int(max_seconds * sample_rate)
        self._deque: deque = deque(maxlen=maxlen)

    def append(self, sample: dict) -> None:
        """Add sample to buffer (drops oldest if full)."""
        self._deque.append(sample)

    def get_window(self, num_samples: int) -> Optional[List[dict]]:
        """
        Return last num_samples as list, or None if insufficient.
        """
        if len(self._deque) < num_samples:
            return None
        # Take last num_samples (newest at end)
        return list(self._deque)[-num_samples:]

    def __len__(self) -> int:
        return len(self._deque)

    def clear(self) -> None:
        """Clear buffer."""
        self._deque.clear()

"""
// Copyright (C) 2025 Matsvei Kuzmiankou
//
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 3 of the License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this program; if not, write to the Free Software Foundation,
// Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import time
from typing import List, Optional
from .Trigger import Trigger
from ..data.TriggerType import TriggerType


class TimestampTrigger(Trigger):
    """Trigger based on specific timestamps"""

    def __init__(self, timestamps: List[int]):
        super().__init__(TriggerType.TIMESTAMP)
        self.timestamps = sorted(timestamps)  # timestamps in milliseconds
        self.current_index = 0

    def get_next_run_time(self, after_time: float = None) -> Optional[float]:
        with self._lock:
            if after_time is None:
                after_time = time.time()

            after_time_ms = after_time * 1000

            while self.current_index < len(self.timestamps):
                if self.timestamps[self.current_index] > after_time_ms:
                    return self.timestamps[self.current_index] / 1000.0
                self.current_index += 1

            return None

    def is_finished(self) -> bool:
        with self._lock:
            return self.current_index >= len(self.timestamps)

    def reset(self):
        with self._lock:
            self.current_index = 0
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
from typing import Optional
from .Trigger import Trigger
from ..data.TriggerType import TriggerType

class IntervalTrigger(Trigger):
    """Trigger based on intervals"""
    def __init__(self, interval_seconds: float, max_runs: Optional[int] = None,
                 start_time: Optional[float] = None):
        super().__init__(TriggerType.INTERVAL)
        self.interval_seconds = interval_seconds
        self.max_runs = max_runs
        self.run_count = 0
        self.start_time = start_time or time.time()
        self.next_run_time = self.start_time

    def get_next_run_time(self, after_time: float = None) -> Optional[float]:
        with self._lock:
            if self.max_runs is not None and self.run_count >= self.max_runs:
                return None

            if after_time is None:
                after_time = time.time()

            # Calculate next run time
            while self.next_run_time <= after_time:
                self.next_run_time += self.interval_seconds

            return self.next_run_time

    def is_finished(self) -> bool:
        with self._lock:
            return self.max_runs is not None and self.run_count >= self.max_runs

    def mark_executed(self):
        with self._lock:
            self.run_count += 1

    def reset(self):
        with self._lock:
            self.run_count = 0
            self.next_run_time = self.start_time

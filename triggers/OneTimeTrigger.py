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
from datetime import datetime
from typing import Union, Optional
from .Trigger import Trigger
from ..data.TriggerType import TriggerType

class OneTimeTrigger(Trigger):
    """Trigger for one-time execution"""
    def __init__(self, run_at: Union[float, datetime]):
        super().__init__(TriggerType.ONE_TIME)
        if isinstance(run_at, datetime):
            self.run_time = run_at.timestamp()
        else:
            self.run_time = run_at
        self.executed = False

    def get_next_run_time(self, after_time: float = None) -> Optional[float]:
        with self._lock:
            if self.executed:
                return None

            if after_time is None:
                after_time = time.time()

            if self.run_time > after_time:
                return self.run_time

            return self.run_time  # Execute immediately if time has passed

    def is_finished(self) -> bool:
        with self._lock:
            return self.executed

    def mark_executed(self):
        with self._lock:
            self.executed = True

    def reset(self):
        with self._lock:
            self.executed = False

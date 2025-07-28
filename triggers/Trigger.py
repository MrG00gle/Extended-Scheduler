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

import threading
from typing import Optional
from ..data.TriggerType import TriggerType


class Trigger:
    """Base class for job triggers"""
    def __init__(self, trigger_type: TriggerType):
        self.trigger_type = trigger_type
        self._lock = threading.RLock()

    def get_next_run_time(self, after_time: float = None) -> Optional[float]:
        """Get the next execution time in seconds since epoch"""
        raise NotImplementedError

    def is_finished(self) -> bool:
        """Check if this trigger has no more executions"""
        raise NotImplementedError

    def reset(self):
        """Reset the trigger to its initial state"""
        raise NotImplementedError

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
import time
from typing import Callable, Dict, Any
from .triggers.Trigger import Trigger
from .data.JobStatus import JobStatus
from .data.TriggerType import TriggerType
from .triggers.TimestampTrigger import TimestampTrigger


class Job:
    """Represents a scheduled job with pause/resume capability"""

    def __init__(self, job_id: str, trigger: Trigger, func: Callable,
                 args: tuple = (), kwargs: dict = None):
        self.job_id = job_id
        self.trigger = trigger
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}

        # State management
        self.status = JobStatus.RUNNING
        self.start_time = None
        self.pause_time = None
        self.total_pause_duration = 0.0
        self.execution_count = 0

        # Threading
        self.thread = None
        self.cancel_event = threading.Event()
        self.pause_event = threading.Event()
        self._lock = threading.RLock()

    def start(self):
        """Start executing the job"""
        with self._lock:
            if self.thread and self.thread.is_alive():
                return False

            self.start_time = time.time()
            self.cancel_event.clear()
            self.pause_event.clear()
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            return True

    def _run(self):
        """Main execution loop"""
        try:
            while not self.trigger.is_finished():
                if self.cancel_event.is_set():
                    break

                # Handle pause
                if self.pause_event.is_set():
                    with self._lock:
                        if self.status == JobStatus.RUNNING:
                            self.status = JobStatus.PAUSED
                            self.pause_time = time.time()

                    # Wait until unpaused or cancelled
                    while self.pause_event.is_set() and not self.cancel_event.is_set():
                        time.sleep(0.01)

                    with self._lock:
                        if self.status == JobStatus.PAUSED and not self.cancel_event.is_set():
                            self.total_pause_duration += time.time() - self.pause_time
                            self.status = JobStatus.RUNNING

                if self.cancel_event.is_set():
                    break

                # Get next execution time
                next_run_time = self.trigger.get_next_run_time()
                if next_run_time is None:
                    break

                # Wait until execution time
                current_time = time.time()
                if self.trigger.trigger_type == TriggerType.TIMESTAMP:
                    # For timestamp triggers, consider pause duration
                    elapsed_real_time = current_time - self.start_time
                    elapsed_execution_time = elapsed_real_time - self.total_pause_duration
                    adjusted_run_time = self.start_time + (next_run_time - self.start_time) + self.total_pause_duration
                    wait_time = adjusted_run_time - current_time
                else:
                    wait_time = next_run_time - current_time

                if wait_time > 0:
                    # Wait with cancellation check
                    end_wait_time = time.time() + wait_time
                    while time.time() < end_wait_time and not self.cancel_event.is_set() and not self.pause_event.is_set():
                        time.sleep(min(0.01, end_wait_time - time.time()))

                if self.cancel_event.is_set() or self.pause_event.is_set():
                    continue

                # Execute the job in a separate thread
                execution_thread = threading.Thread(
                    target=self._execute_job,
                    daemon=True
                )
                execution_thread.start()

                # Mark execution
                self.execution_count += 1
                if hasattr(self.trigger, 'mark_executed'):
                    self.trigger.mark_executed()

                # For timestamp trigger, advance the index
                if isinstance(self.trigger, TimestampTrigger):
                    self.trigger.current_index += 1

            # Mark as completed if not cancelled
            with self._lock:
                if self.status != JobStatus.REMOVED:
                    self.status = JobStatus.COMPLETED

        except Exception as e:
            print(f"Error in job {self.job_id}: {e}")

    def _execute_job(self):
        """Execute the actual job function"""
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as e:
            print(f"Error executing job {self.job_id}: {e}")

    def pause(self) -> bool:
        """Pause the job"""
        with self._lock:
            if self.status == JobStatus.RUNNING:
                self.pause_event.set()
                return True
            return False

    def resume(self) -> bool:
        """Resume the job"""
        with self._lock:
            if self.status == JobStatus.PAUSED or self.pause_event.is_set():
                self.pause_event.clear()
                return True
            return False

    def cancel(self):
        """Cancel the job"""
        with self._lock:
            self.status = JobStatus.REMOVED
            self.cancel_event.set()
            self.pause_event.clear()

    def get_status(self) -> Dict[str, Any]:
        """Get current job status"""
        with self._lock:
            elapsed_time = 0
            if self.start_time:
                elapsed_time = (time.time() - self.start_time - self.total_pause_duration) * 1000

            next_run_time = self.trigger.get_next_run_time()

            return {
                'job_id': self.job_id,
                'status': self.status.value,
                'trigger_type': self.trigger.trigger_type.value,
                'execution_count': self.execution_count,
                'elapsed_time_ms': elapsed_time,
                'next_run_time': next_run_time,
                'is_finished': self.trigger.is_finished()
            }

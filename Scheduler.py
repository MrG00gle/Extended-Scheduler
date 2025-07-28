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
from datetime import datetime
from typing import Dict, Callable, List, Optional, Union, Any

from .Job import Job
from .triggers.Trigger import Trigger
from .triggers.TimestampTrigger import TimestampTrigger
from .triggers.IntervalTrigger import IntervalTrigger
from .triggers.OneTimeTrigger import OneTimeTrigger
from .triggers.CronTrigger import CronTrigger

class Scheduler:
    """Advanced scheduler with multiple triggering mechanisms"""

    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self._lock = threading.RLock()

    def add_job(self, job_id: str, trigger: Trigger, func: Callable,
                *args, **kwargs) -> bool:
        """
        Add a job to the scheduler with a specific trigger

        Args:
            job_id: Unique identifier for the job
            trigger: Trigger instance defining when to execute
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            True if job was added successfully, False if job with this ID already exists
        """
        with self._lock:
            if job_id in self.jobs:
                return False

            job = Job(job_id, trigger, func, args, kwargs)
            self.jobs[job_id] = job
            job.start()
            return True

    def add_timestamp_job(self, job_id: str, timestamps: List[int],
                          func: Callable, *args, **kwargs) -> bool:
        """Add a job with timestamp-based trigger"""
        trigger = TimestampTrigger(timestamps)
        return self.add_job(job_id, trigger, func, *args, **kwargs)

    def add_interval_job(self, job_id: str, interval_seconds: float,
                         func: Callable, max_runs: Optional[int] = None,
                         start_time: Optional[float] = None,
                         *args, **kwargs) -> bool:
        """Add a job with interval-based trigger"""
        trigger = IntervalTrigger(interval_seconds, max_runs, start_time)
        return self.add_job(job_id, trigger, func, *args, **kwargs)

    def add_one_time_job(self, job_id: str, run_at: Union[float, datetime],
                         func: Callable, *args, **kwargs) -> bool:
        """Add a one-time job"""
        trigger = OneTimeTrigger(run_at)
        return self.add_job(job_id, trigger, func, *args, **kwargs)

    def add_cron_job(self, job_id: str, cron_expression: str,
                     func: Callable, max_runs: Optional[int] = None,
                     timezone: str = 'UTC', start_time: Optional[datetime] = None,
                     *args, **kwargs) -> bool:
        """Add a job with cron-based trigger"""
        trigger = CronTrigger(cron_expression, max_runs, timezone, start_time)
        return self.add_job(job_id, trigger, func, *args, **kwargs)

    def pause_job(self, job_id: str) -> bool:
        """Pause a job"""
        with self._lock:
            job = self.jobs.get(job_id)
            if job:
                return job.pause()
            return False

    def resume_job(self, job_id: str) -> bool:
        """Resume a paused job"""
        with self._lock:
            job = self.jobs.get(job_id)
            if job:
                return job.resume()
            return False

    def remove_job(self, job_id: str) -> bool:
        """Remove a job from the scheduler"""
        with self._lock:
            job = self.jobs.get(job_id)
            if job:
                job.cancel()
                del self.jobs[job_id]
                return True
            return False

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a job"""
        with self._lock:
            job = self.jobs.get(job_id)
            if job:
                return job.get_status()
            return None

    def list_jobs(self) -> List[str]:
        """Get a list of all job IDs"""
        with self._lock:
            return list(self.jobs.keys())

    def get_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all jobs"""
        with self._lock:
            return {job_id: job.get_status() for job_id, job in self.jobs.items()}

    def shutdown(self):
        """Shutdown the scheduler and cancel all jobs"""
        with self._lock:
            for job in self.jobs.values():
                job.cancel()
            self.jobs.clear()


# Example usage and demonstration
if __name__ == "__main__":
    def example_job(message: str, job_id: str = "unknown"):
        current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{current_time}] Job {job_id} executed: {message}")

    # Create scheduler
    scheduler = Scheduler()

    # 1. Timestamp-based job (original functionality)
    print("=== TIMESTAMP TRIGGER ===")
    timestamps = [0, 200, 500, 1000]
    scheduler.add_timestamp_job("timestamp_job", timestamps, example_job,
                                "Timestamp trigger", job_id="timestamp_job")

    # 2. Interval-based job
    print("\n=== INTERVAL TRIGGER ===")
    scheduler.add_interval_job("interval_job", 0.5, example_job,
                               max_runs=5,
                               message="Interval trigger (every 0.5s)",
                               job_id="interval_job")

    # 3. One-time job
    print("\n=== ONE-TIME TRIGGER ===")
    run_time = time.time() + 2  # Run after 2 seconds
    scheduler.add_one_time_job("onetime_job", run_time, example_job,
                               "One-time trigger", job_id="onetime_job")

    # 4. Cron-based job (every 2 seconds, max 3 times)
    print("\n=== CRON TRIGGER ===")
    scheduler.add_cron_job("cron_job", "*/2 * * * * *", example_job,
                           max_runs=3,
                           message="Cron trigger (every 2 seconds)",
                           job_id="cron_job")

    # Let jobs run for a bit
    time.sleep(3)

    # Show status
    print("\n=== JOB STATUSES ===")
    for job_id, status in scheduler.get_all_statuses().items():
        print(f"{job_id}: {status}")

    # Test pause/resume on interval job
    print("\n=== TESTING PAUSE/RESUME ===")
    scheduler.pause_job("interval_job")
    print("Interval job paused")
    time.sleep(2)
    scheduler.resume_job("interval_job")
    print("Interval job resumed")

    # Let everything complete
    time.sleep(5)

    # Final status
    print("\n=== FINAL STATUSES ===")
    for job_id, status in scheduler.get_all_statuses().items():
        print(f"{job_id}: {status}")

    scheduler.shutdown()
    print("\nScheduler shutdown complete")

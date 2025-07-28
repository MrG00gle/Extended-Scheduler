# Extednded Scheduler Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)
5. [Trigger Types](#trigger-types)
6. [API Reference](#api-reference)
7. [Examples](#examples)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Overview

The Extednded Scheduler is a flexible, thread-safe scheduling library that supports multiple triggering mechanisms including timestamps, intervals, one-time execution, and cron expressions. Key features include:

- **Multiple Trigger Types**: Timestamp, interval, one-time, and cron-based scheduling
- **Pause/Resume Capability**: Full control over job execution flow
- **Thread-Safe**: Safe for concurrent operations
- **Flexible**: Easy to extend with custom trigger types
- **Reliable**: Robust error handling and state management

## Installation

### Requirements
- Python 3.7+
- Dependencies:
  ```bash
  pip install croniter pytz
  ```

### Basic Installation
```python
# Copy the scheduler module to your project
# Import the required classes
from scheduler import Scheduler, TimestampTrigger, IntervalTrigger, OneTimeTrigger, CronTrigger
```

## Quick Start

```python
from scheduler import Scheduler
import time

# Create a scheduler instance
scheduler = Scheduler()

# Define a simple job function
def print_message(msg):
    print(f"Job executed: {msg}")

# Add an interval job that runs every 2 seconds
scheduler.add_interval_job("heartbeat", 2.0, print_message, "Hello World!")

# Let it run for 10 seconds
time.sleep(10)

# Cleanup
scheduler.shutdown()
```

## Core Concepts

### Jobs
A job represents a scheduled task with:
- Unique identifier
- Trigger mechanism
- Function to execute
- Arguments and keyword arguments
- Execution state tracking

### Triggers
Triggers determine when a job should execute. The library includes four built-in trigger types:
- `TimestampTrigger`: Execute at specific timestamps
- `IntervalTrigger`: Execute at regular intervals
- `OneTimeTrigger`: Execute once at a specified time
- `CronTrigger`: Execute based on cron expressions

### Job States
Jobs can be in one of four states:
- `RUNNING`: Actively executing or waiting for next execution
- `PAUSED`: Temporarily suspended
- `COMPLETED`: Finished all executions
- `REMOVED`: Cancelled and removed from scheduler

## Trigger Types

### TimestampTrigger
Executes a job at specific timestamps (in milliseconds).

```python
# Execute at 0ms, 500ms, 1000ms, and 2000ms
timestamps = [0, 500, 1000, 2000]
trigger = TimestampTrigger(timestamps)
```

**Use Cases:**
- Synchronized animations
- Timed sequences
- Replay systems

### IntervalTrigger
Executes a job at regular intervals.

```python
# Execute every 5 seconds, maximum 10 times
trigger = IntervalTrigger(
    interval_seconds=5.0,
    max_runs=10,  # Optional: limit executions
    start_time=time.time() + 10  # Optional: delay start by 10 seconds
)
```

**Use Cases:**
- Periodic health checks
- Data synchronization
- Regular cleanup tasks

### OneTimeTrigger
Executes a job once at a specified time.

```python
# Execute in 30 seconds
trigger = OneTimeTrigger(time.time() + 30)

# Or use datetime
from datetime import datetime, timedelta
run_at = datetime.now() + timedelta(hours=1)
trigger = OneTimeTrigger(run_at)
```

**Use Cases:**
- Delayed notifications
- Scheduled reports
- Time-based reminders

### CronTrigger
Executes a job based on cron expressions.

```python
# Execute every weekday at 9:00 AM
trigger = CronTrigger(
    cron_expression="0 9 * * MON-FRI",
    max_runs=None,  # Optional: no limit
    timezone="America/New_York",  # Optional: timezone aware
    start_time=datetime.now()  # Optional: custom start time
)
```

**Cron Expression Format:**
```
* * * * * *
│ │ │ │ │ │
│ │ │ │ │ └─ Day of week (0-7, MON-SUN)
│ │ │ │ └─── Month (1-12)
│ │ │ └───── Day of month (1-31)
│ │ └─────── Hour (0-23)
│ └───────── Minute (0-59)
└─────────── Second (0-59)  [Optional]
```

**Use Cases:**
- Daily backups
- Weekly reports
- Business hours operations

## API Reference

### Scheduler Class

#### `__init__()`
Creates a new scheduler instance.

```python
scheduler = Scheduler()
```

#### `add_job(job_id, trigger, func, *args, **kwargs)`
Adds a job with a custom trigger.

**Parameters:**
- `job_id` (str): Unique identifier for the job
- `trigger` (Trigger): Trigger instance defining execution schedule
- `func` (Callable): Function to execute
- `*args`: Positional arguments for the function
- `**kwargs`: Keyword arguments for the function

**Returns:** `bool` - True if successful, False if job_id already exists

```python
trigger = IntervalTrigger(5.0)
scheduler.add_job("my_job", trigger, my_function, arg1, arg2, key1="value1")
```

#### `add_timestamp_job(job_id, timestamps, func, *args, **kwargs)`
Convenience method for timestamp-based jobs.

**Parameters:**
- `timestamps` (List[int]): List of timestamps in milliseconds

```python
scheduler.add_timestamp_job("animation", [0, 100, 200, 300], animate_frame)
```

#### `add_interval_job(job_id, interval_seconds, func, max_runs=None, start_time=None, *args, **kwargs)`
Convenience method for interval-based jobs.

**Parameters:**
- `interval_seconds` (float): Seconds between executions
- `max_runs` (int, optional): Maximum number of executions
- `start_time` (float, optional): Unix timestamp to start

```python
scheduler.add_interval_job("heartbeat", 1.0, check_health, max_runs=60)
```

#### `add_one_time_job(job_id, run_at, func, *args, **kwargs)`
Convenience method for one-time jobs.

**Parameters:**
- `run_at` (float or datetime): When to execute

```python
scheduler.add_one_time_job("reminder", datetime.now() + timedelta(hours=1), send_reminder)
```

#### `add_cron_job(job_id, cron_expression, func, max_runs=None, timezone='UTC', start_time=None, *args, **kwargs)`
Convenience method for cron-based jobs.

**Parameters:**
- `cron_expression` (str): Cron expression string
- `max_runs` (int, optional): Maximum number of executions
- `timezone` (str): Timezone name (e.g., 'America/New_York')
- `start_time` (datetime, optional): Custom start time

```python
scheduler.add_cron_job("backup", "0 2 * * *", backup_database, timezone="UTC")
```

#### `pause_job(job_id)`
Pauses a running job.

**Returns:** `bool` - True if successful

```python
scheduler.pause_job("my_job")
```

#### `resume_job(job_id)`
Resumes a paused job.

**Returns:** `bool` - True if successful

```python
scheduler.resume_job("my_job")
```

#### `remove_job(job_id)`
Removes and cancels a job.

**Returns:** `bool` - True if successful

```python
scheduler.remove_job("my_job")
```

#### `get_job_status(job_id)`
Gets detailed status of a job.

**Returns:** `dict` or `None`

```python
status = scheduler.get_job_status("my_job")
# Returns:
# {
#     'job_id': 'my_job',
#     'status': 'running',
#     'trigger_type': 'interval',
#     'execution_count': 5,
#     'elapsed_time_ms': 25000,
#     'next_run_time': 1640000000.0,
#     'is_finished': False
# }
```

#### `list_jobs()`
Gets list of all job IDs.

**Returns:** `List[str]`

```python
job_ids = scheduler.list_jobs()
```

#### `get_all_statuses()`
Gets status of all jobs.

**Returns:** `Dict[str, dict]`

```python
all_statuses = scheduler.get_all_statuses()
```

#### `shutdown()`
Stops all jobs and cleans up resources.

```python
scheduler.shutdown()
```

## Examples

### Example 1: Data Collection Pipeline

```python
from scheduler import Scheduler
import requests
import json
from datetime import datetime

scheduler = Scheduler()

def collect_data(source_name):
    """Collect data from an API"""
    response = requests.get(f"https://api.example.com/{source_name}")
    data = response.json()
    
    with open(f"data_{source_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(data, f)
    
    print(f"Data collected from {source_name}")

def process_data():
    """Process collected data"""
    print("Processing all collected data...")
    # Processing logic here

def cleanup_old_data():
    """Remove data older than 7 days"""
    print("Cleaning up old data files...")
    # Cleanup logic here

# Collect data every 5 minutes
scheduler.add_interval_job("collect_api1", 300, collect_data, "api1")
scheduler.add_interval_job("collect_api2", 300, collect_data, "api2")

# Process data every hour
scheduler.add_cron_job("process", "0 * * * *", process_data)

# Cleanup daily at 2 AM
scheduler.add_cron_job("cleanup", "0 2 * * *", cleanup_old_data)

# Run for 24 hours
import time
time.sleep(86400)
scheduler.shutdown()
```

### Example 2: Notification System

```python
from scheduler import Scheduler
from datetime import datetime, timedelta

scheduler = Scheduler()

def send_notification(user_id, message, notification_type="info"):
    """Send notification to user"""
    print(f"[{notification_type.upper()}] User {user_id}: {message}")
    # Actual notification logic here

# Immediate notification
scheduler.add_one_time_job(
    "urgent_notice", 
    time.time() + 5,  # 5 seconds from now
    send_notification, 
    123, 
    "Your order has been shipped!",
    notification_type="success"
)

# Reminder in 1 hour
scheduler.add_one_time_job(
    "appointment_reminder",
    datetime.now() + timedelta(hours=1),
    send_notification,
    456,
    "You have an appointment in 30 minutes",
    notification_type="warning"
)

# Daily summary at 6 PM
scheduler.add_cron_job(
    "daily_summary",
    "0 18 * * *",
    send_notification,
    789,
    "Here's your daily activity summary",
    notification_type="info"
)
```

### Example 3: Animation Sequence with Pause/Resume

```python
from scheduler import Scheduler
import time

scheduler = Scheduler()

def animate_frame(frame_number, object_id):
    """Render animation frame"""
    print(f"Rendering frame {frame_number} for object {object_id}")
    # Animation logic here

# Create animation sequence (60 fps for 2 seconds = 120 frames)
timestamps = [int(i * 1000/60) for i in range(120)]  # Timestamps in ms

scheduler.add_timestamp_job(
    "animation_1",
    timestamps,
    animate_frame,
    frame_number_placeholder,  # Will use timestamp index
    object_id="ball"
)

# Let it run for 500ms
time.sleep(0.5)

# Pause the animation
scheduler.pause_job("animation_1")
print("Animation paused")

# Wait 2 seconds
time.sleep(2)

# Resume the animation
scheduler.resume_job("animation_1")
print("Animation resumed")

# Let it complete
time.sleep(3)
scheduler.shutdown()
```

### Example 4: Business Hours Operations

```python
from scheduler import Scheduler

scheduler = Scheduler()

def start_business_operations():
    """Initialize business hours operations"""
    print("Starting business operations")
    # Start services, open connections, etc.

def stop_business_operations():
    """Shutdown business hours operations"""
    print("Stopping business operations")
    # Stop services, close connections, etc.

def process_orders():
    """Process pending orders"""
    print("Processing orders...")
    # Order processing logic

# Start operations Monday-Friday at 9 AM
scheduler.add_cron_job(
    "business_start",
    "0 9 * * MON-FRI",
    start_business_operations,
    timezone="America/New_York"
)

# Stop operations Monday-Friday at 5 PM
scheduler.add_cron_job(
    "business_stop",
    "0 17 * * MON-FRI",
    stop_business_operations,
    timezone="America/New_York"
)

# Process orders every 30 minutes during business hours
scheduler.add_cron_job(
    "order_processing",
    "*/30 9-16 * * MON-FRI",
    process_orders,
    timezone="America/New_York"
)
```

## Best Practices

### 1. Job ID Management
- Use descriptive, unique job IDs
- Consider using UUIDs for dynamically created jobs
- Implement a naming convention (e.g., `module_function_purpose`)

```python
import uuid

job_id = f"data_sync_{uuid.uuid4().hex[:8]}"
```

### 2. Error Handling
- Jobs should handle their own exceptions
- Use try-except blocks in job functions
- Log errors appropriately

```python
def safe_job_function():
    try:
        # Job logic here
        risky_operation()
    except Exception as e:
        logger.error(f"Job failed: {e}")
        # Optionally notify monitoring system
```

### 3. Resource Management
- Always call `shutdown()` when done
- Use context managers for scheduler lifecycle
- Monitor memory usage for long-running schedulers

```python
class SchedulerContext:
    def __enter__(self):
        self.scheduler = Scheduler()
        return self.scheduler
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.scheduler.shutdown()

# Usage
with SchedulerContext() as scheduler:
    scheduler.add_interval_job("job1", 1.0, my_function)
    # Scheduler operations
# Automatically cleaned up
```

### 4. Timezone Awareness
- Always specify timezone for cron jobs
- Use UTC for coordination across time zones
- Be explicit about daylight saving time handling

```python
# Good practice
scheduler.add_cron_job("report", "0 14 * * *", generate_report, timezone="UTC")

# For local time
import pytz
local_tz = pytz.timezone("America/Chicago")
scheduler.add_cron_job("local_task", "0 8 * * *", morning_task, timezone="America/Chicago")
```

### 5. Testing Strategies
- Use shorter intervals for testing
- Mock time-dependent operations
- Test pause/resume functionality

```python
def test_scheduler():
    scheduler = Scheduler()
    executions = []
    
    def test_job(job_id):
        executions.append((job_id, time.time()))
    
    # Add job with short interval
    scheduler.add_interval_job("test", 0.1, test_job, "test", max_runs=5)
    
    time.sleep(0.6)
    assert len(executions) == 5
    scheduler.shutdown()
```

## Troubleshooting

### Common Issues

#### 1. Job Not Executing
**Symptoms:** Job added but function never called

**Possible Causes:**
- Scheduler not running (forgot to keep main thread alive)
- Job scheduled for future time
- Job already completed (check `is_finished`)

**Solution:**
```python
# Check job status
status = scheduler.get_job_status("my_job")
print(f"Status: {status['status']}")
print(f"Next run: {status['next_run_time']}")
print(f"Is finished: {status['is_finished']}")

# Ensure main thread stays alive
while True:
    time.sleep(1)
    # Or use more sophisticated event loop
```

#### 2. Memory Leaks
**Symptoms:** Memory usage grows over time

**Possible Causes:**
- Not removing completed jobs
- Job functions holding references
- Large data in job arguments

**Solution:**
```python
# Periodically clean up completed jobs
def cleanup_completed_jobs(scheduler):
    for job_id in scheduler.list_jobs():
        status = scheduler.get_job_status(job_id)
        if status and status['status'] == 'completed':
            scheduler.remove_job(job_id)

# Schedule cleanup
scheduler.add_interval_job("cleanup", 3600, cleanup_completed_jobs, scheduler)
```

#### 3. Timezone Issues
**Symptoms:** Cron jobs execute at wrong time

**Possible Causes:**
- Server timezone different from expected
- Daylight saving time transitions
- Incorrect timezone specification

**Solution:**
```python
# Always be explicit about timezone
import pytz
from datetime import datetime

# Check server timezone
print(f"Server timezone: {datetime.now().astimezone().tzinfo}")

# List available timezones
print("Available timezones:", pytz.all_timezones[:10])  # First 10

# Use explicit timezone
scheduler.add_cron_job(
    "daily_task",
    "0 9 * * *",
    my_task,
    timezone="Europe/London"  # Explicit timezone
)
```

#### 4. Thread Safety Issues
**Symptoms:** Inconsistent state, race conditions

**Possible Causes:**
- Accessing scheduler from multiple threads without synchronization
- Modifying shared data in job functions

**Solution:**
```python
# Use thread-safe operations
import threading

shared_data = []
data_lock = threading.Lock()

def thread_safe_job():
    with data_lock:
        shared_data.append(datetime.now())
    
    # Or use thread-safe data structures
    from queue import Queue
    result_queue = Queue()
    result_queue.put("result")
```

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add debug prints to job functions
def debug_job(job_id):
    logger = logging.getLogger(__name__)
    logger.debug(f"Job {job_id} starting")
    # Job logic
    logger.debug(f"Job {job_id} completed")
```

### Performance Monitoring

```python
import psutil
import os

def monitor_scheduler_performance():
    process = psutil.Process(os.getpid())
    
    return {
        'memory_usage_mb': process.memory_info().rss / 1024 / 1024,
        'cpu_percent': process.cpu_percent(interval=1),
        'num_threads': process.num_threads(),
        'active_jobs': len([j for j in scheduler.list_jobs() 
                           if scheduler.get_job_status(j)['status'] == 'running'])
    }

# Schedule monitoring
scheduler.add_interval_job(
    "monitor",
    60,  # Every minute
    lambda: print(monitor_scheduler_performance())
)
```

## Contributing

When extending the scheduler:

1. **Create New Trigger Types**
```python
class RandomIntervalTrigger(Trigger):
    def __init__(self, min_seconds, max_seconds):
        super().__init__(TriggerType.CUSTOM)
        self.min_seconds = min_seconds
        self.max_seconds = max_seconds
        self.next_time = None
    
    def get_next_run_time(self, after_time=None):
        if after_time is None:
            after_time = time.time()
        
        if self.next_time is None or self.next_time <= after_time:
            import random
            delay = random.uniform(self.min_seconds, self.max_seconds)
            self.next_time = after_time + delay
        
        return self.next_time
    
    def is_finished(self):
        return False  # Never finishes
```

2. **Add Job Decorators**
```python
def scheduled_job(trigger):
    def decorator(func):
        job_id = f"{func.__module__}.{func.__name__}"
        scheduler.add_job(job_id, trigger, func)
        return func
    return decorator

# Usage
@scheduled_job(IntervalTrigger(60))
def automated_task():
    print("This runs every minute")
```
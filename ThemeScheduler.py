#!/usr/bin/env python3
"""
ThemeScheduler module - Handles automatic theme switching based on sunrise/sunset times.
Separates scheduling logic from UI concerns.
"""
import sched
import time
import datetime
import threading
from typing import Callable, Optional
import SunJob as sunjob


class ThemeScheduler:
    """Manages automatic theme switching based on sunrise/sunset."""
    
    def __init__(self) -> None:
        """Initialize the theme scheduler."""
        self.scheduler: sched.scheduler = sched.scheduler(time.time, time.sleep)
        self.current_event: Optional[sched.Event] = None
        self._scheduler_thread: Optional[threading.Thread] = None
        self.next_event_time: Optional[datetime.datetime] = None
        self.next_event_type: Optional[str] = None
    
    def schedule_initial_event(
        self, 
        on_sunrise: Callable[[], None],
        on_sunset: Callable[[], None]
    ) -> None:
        """
        Schedule the first event based on current time and sunrise/sunset times.
        
        Args:
            on_sunrise: Callback to execute at sunrise.
            on_sunset: Callback to execute at sunset.
        """
        now = datetime.datetime.now()
        sunrise = datetime.datetime.strptime(sunjob.get_sunrise_local(), "%H:%M").time()
        sunset = datetime.datetime.strptime(sunjob.get_sunset_local(), "%H:%M").time()
        
        # Determine if it's currently day or night
        if sunrise <= now.time() < sunset:
            next_event = "sunset"
        else:
            next_event = "sunrise"
        
        self.schedule_event(next_event, on_sunrise, on_sunset)
    
    def schedule_event(
        self,
        event_type: str,
        on_sunrise: Callable[[], None],
        on_sunset: Callable[[], None]
    ) -> None:
        """
        Schedule a sunrise or sunset event.
        
        This method calculates the time until the next sunrise or sunset,
        schedules the callback, and ensures the scheduler thread is running.
        
        Args:
            event_type: Either 'sunrise' or 'sunset'.
            on_sunrise: Callback to execute at sunrise.
            on_sunset: Callback to execute at sunset.
        """
        def switch_and_reschedule() -> None:
            # Execute the appropriate callback and schedule the next event
            if event_type == "sunset":
                on_sunset()
                self.schedule_event("sunrise", on_sunrise, on_sunset)
            else:
                on_sunrise()
                self.schedule_event("sunset", on_sunrise, on_sunset)
        
        now = datetime.datetime.now()
        # Get the scheduled time for this event type
        event_time_str = (
            sunjob.get_sunset_local() 
            if event_type == "sunset" 
            else sunjob.get_sunrise_local()
        )
        event_time = datetime.datetime.strptime(event_time_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        
        # Adjust for tomorrow if the event time has already passed today
        if event_time < now:
            event_time += datetime.timedelta(days=1)
        
        delay: float = (event_time - now).total_seconds()
        
        # Store next event information for UI display
        self.next_event_time = event_time
        self.next_event_type = event_type
        
        # Cancel previous event if it exists to avoid duplicates
        if self.current_event:
            self.scheduler.cancel(self.current_event)
        
        # Schedule the new event using Python's sched module
        self.current_event = self.scheduler.enter(delay, 1, switch_and_reschedule, ())
        
        # Start scheduler thread if not already running
        if self._scheduler_thread is None or not self._scheduler_thread.is_alive():
            self._scheduler_thread = threading.Thread(
                target=self.scheduler.run, 
                daemon=True
            )
            self._scheduler_thread.start()
        return event_time
    
    def cancel_all_events(self) -> None:
        """Cancel all scheduled events."""
        for event in list(self.scheduler.queue):
            self.scheduler.cancel(event)
        self.current_event = None
        self.next_event_time = None
        self.next_event_type = None
    
    def is_running(self) -> bool:
        """Check if there are pending scheduled events."""
        return len(self.scheduler.queue) > 0
    
    def get_next_event_info(self) -> tuple[Optional[str], Optional[str]]:
        """
        Get information about the next scheduled event.
        
        Returns:
            tuple: (event_type, time_str) or (None, None) if no event scheduled.
                   event_type: 'sunrise' or 'sunset'
                   time_str: Time in HH:MM format
        """
        if self.next_event_time is None or self.next_event_type is None:
            return None, None
        
        time_str = self.next_event_time.strftime("%H:%M")
        event_label = "🌅 Amanecer" if self.next_event_type == "sunrise" else "🌅 Anochecer"
        return event_label, time_str

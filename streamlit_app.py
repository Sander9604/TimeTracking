import streamlit as st
import threading
import time
from datetime import datetime, timedelta

# 1. Define the Timer structure and Server State
class TimerData:
    def __init__(self, name, duration):
        self.name = name
        self.total_duration = duration # The reset value (e.g., 60 seconds)
        self.remaining = duration      # Current seconds left (e.g., 45.5)
        self.end_time = None           # Timestamp when timer finishes (if running)
        self.is_running = False

class ServerState:
    def __init__(self):
        # Existing counters/logs
        self.counter = 0
        self.logs = []
        
        # New: Store timers in a dictionary by ID
        # Format: { "timer_1": TimerData object, ... }
        self.timers = {} 
        self._lock = threading.Lock()

    # --- Existing Counter/Log Methods ---
    def increment(self):
        with self._lock:
            self.counter += 1
            self._log(f"Counter incremented to {self.counter}")

    def decrement(self):
        with self._lock:
            self.counter -= 1
            self._log(f"Counter decremented to {self.counter}")

    def add_message(self, user, message):
        with self._lock:
            self._log(f"Message from {user}: {message}")

    def _log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
        # Keep logs limited to avoid infinite growth. Increased limit for better visibility.
        if len(self.logs) > 50:
            self.logs.pop(0)

    # --- New Timer Methods ---
    def create_timer(self, timer_id, name, duration):
        with self._lock:
            if timer_id not in self.timers:
                self.timers[timer_id] = TimerData(name, duration)

    def start_timer(self, timer_id):
        with self._lock:
            t = self.timers.get(timer_id)
            if t and not t.is_running:
                # Calculate exactly when this timer will finish
                t.end_time = datetime.now() + timedelta(seconds=t.remaining)
                t.is_running = True
                self._log(f"Started {t.name}")

    def stop_timer(self, timer_id):
        with self._lock:
            t = self.timers.get(timer_id)
            if t and t.is_running:
                # Calculate how much time was left when stopped
                now = datetime.now()
                delta = (t.end_time - now).total_seconds()
                t.remaining = max(0, delta)
                t.is_running = False
                t.end_time = None
                self._log(f"Stopped {t.name}")

    def reset_timer(self, timer_id):
        with self._lock:
            t = self.timers.get(timer_id)
            if t:
                t.remaining = t.total_duration
                t.is_running = False
                t.end_time = None
                self._log(f"Reset {t.name}")

    def update_duration(self, timer_id, new_duration):
        with self._lock:
            t = self.timers.get(timer_id)
            if t:
                t.total_duration = new_duration
                t.remaining = new_duration
                t.is_running = False
                t.end_time = None
                self._log(f"Updated {t.name} to {new_duration}s")

    def update_and_get_timer(self, timer_id):
        """
        Calculates the current state of the timer. 
        If expired, auto-restarts it inside the lock.
        Returns: (remaining_time, total_duration, is_running, just_finished) - ALWAYS 4 VALUES
        """
        with self._lock:
            t = self.timers.get(timer_id)
            if not t:
                # 4 values returned
                return 0, 100, False, False 
            
            if t.is_running:
                now = datetime.now()
                remaining = (t.end_time - now).total_seconds()
                
                if remaining <= 0:
                    # Timer Reached Zero: AUTO-RESTART LOGIC
                    
                    # 1. Flag that it just finished
                    just_finished = True 
                    
                    # 2. Recalculate end_time for the new cycle (starts instantly)
                    t.end_time = datetime.now() + timedelta(seconds=t.total_duration)
                    t.remaining = t.total_duration # Resets the visible remaining time
                    t.is_running = True # Remains running
                    
                    self._log(f"{t.name} finished and automatically restarted")
                    
                    # Recalculate remaining time for the *new* cycle (will be slightly less than total_duration)
                    new_remaining = (t.end_time - datetime.now()).total_seconds() 
                    
                    # 4 values returned: new_remaining, total_duration, True (running), True (just finished)
                    return new_remaining, t.total_duration, True, just_finished 
                else:
                    # Timer is actively running
                    # 4 values returned
                    return remaining, t.total_duration, True, False # running, not finished
            else:
                # Timer is paused
                # 4 values returned
                return t.remaining, t.total_duration, False, False # not running, not finished

# 2. Singleton Initialization
# Renaming this function again forces Streamlit to create a new cache entry
# and instantiate the NEW ServerState class, resolving caching issues.
@st.cache_resource
def get_shared_state_v5():
    state = ServerState()
    # Initialize some default timers if they don't exist
    state.create_timer("t1", "Frames", 60) 
    state.create_timer("t2", '12"', 300) 
    state.create_timer("t3", "Plugs", 60)
    state.create_timer("t4", "Plug Material", 60)
    return state

# 3. Main App Logic
def main():
    st.set_page_config(page_title="Global Shared State", layout="centered")
    
    st.title("🌐 Server-Wide Shared App")
    st.markdown("Open multiple tabs to see these values sync in real-time.")

    # Call the V5 function to get the fresh instance
    shared_state = get_shared_state_v5()
    
    # --- Check if we need to auto-refresh (animation loop) ---
    any_timer_running = False
    
    # --- Section 1: Timers ---
    st.header("⏱️ Shared Timers")
    
    timer_ids = ["t1", "t2", "t3", "t4"]
    
    # Create two primary columns to hold the timers side-by-side
    col_left, col_right = st.columns(2)

    for i, tid in enumerate(timer_ids):
        # Determine the target column: t1 and t2 go left (index 0, 1), t3 and t4 go right (index 2, 3)
        target_col = col_left if i < 2 else col_right

        with target_col:
            # Get up-to-date values (thread-safe)
            # We now unpack four values: rem, total, running, just_finished
            rem, total, running, just_finished = shared_state.update_and_get_timer(tid)
            name = shared_state.timers[tid].name
            
            if running:
                any_timer_running = True
                
            # Display the toast notification immediately when a timer finishes
            if just_finished:
                st.toast(f"✅ Timer '{name}' has completed and automatically restarted!", icon="🔄")

            # Timer UI Card
            with st.container(border=True):
                # Inner columns for metrics/progress vs. buttons
                c1, c2 = st.columns([3, 1]) 
                with c1:
                    st.subheader(f"{name}")
                    # Format time as MM:SS
                    mins, secs = divmod(int(rem), 60)
                    time_str = f"{mins:02d}:{secs:02d}"
                    # The metric delta shows the current status clearly
                    st.metric("Time Remaining", time_str, delta="Running" if running else "Paused")
                    
                    # Progress Bar
                    # Avoid division by zero if duration is 0
                    if total > 0:
                        progress = max(0.0, min(1.0, rem / total))
                    else:
                        progress = 0.0
                    st.progress(progress)
                    
                    with st.expander("⚙️ Settings"):
                        new_duration = st.number_input(
                            "Duration (seconds)", 
                            min_value=1, 
                            value=int(total), 
                            step=10, 
                            key=f"dur_{tid}"
                        )
                        if st.button("Set Duration", key=f"set_{tid}", use_container_width=True):
                            shared_state.update_duration(tid, new_duration)
                            st.rerun()

                with c2:
                    st.write("##") # Spacer for alignment
                    if running:
                        if st.button("Stop", key=f"stop_{tid}", type="primary", use_container_width=True):
                            shared_state.stop_timer(tid)
                            st.rerun()
                    else:
                        if st.button("Start", key=f"start_{tid}", use_container_width=True):
                            shared_state.start_timer(tid)
                            st.rerun()
                    
                    # Moved Reset button down to align with the Start/Stop button
                    if st.button("Reset", key=f"rst_{tid}", use_container_width=True):
                        shared_state.reset_timer(tid)
                        st.rerun()

    # --- Section 2: Shared Counter (Preserved) ---
    st.divider()
    with st.expander("See Shared Counter & Logs"):
        st.header("Shared Counter")
        st.metric(label="Global Count", value=shared_state.counter)

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("➕ Increment"):
                shared_state.increment()
                st.rerun()
        with col2:
            if st.button("➖ Decrement"):
                shared_state.decrement()
                st.rerun()
        with col3:
            if st.button("Refresh Log"):
                st.rerun()

        st.subheader("Activity Log")
        for log in reversed(shared_state.logs):
            st.text(log)

    # --- Animation Loop ---
    # If a timer is running, we sleep briefly and rerun to update the progress bar.
    if any_timer_running:
        # Sleep for less than a second to ensure smooth countdown animation
        time.sleep(0.1) 
        st.rerun()

if __name__ == "__main__":
    main()

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

    def restart_timer(self, timer_id):
        """Resets the time to total_duration and starts the timer immediately."""
        with self._lock:
            t = self.timers.get(timer_id)
            if t:
                t.remaining = t.total_duration
                # Key change: Calculate new end time and set to running
                t.end_time = datetime.now() + timedelta(seconds=t.total_duration)
                t.is_running = True
                self._log(f"Restarted {t.name}")

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
@st.cache_resource
def get_shared_state_v9(): # Bumped version for new features
    state = ServerState()
    # Initialize some default timers if they don't exist
    state.create_timer("t1", "Frames", 60) 
    state.create_timer("t2", '12"', 300) 
    state.create_timer("t3", "Plugs", 60)
    state.create_timer("t4", "Plug Material", 60)
    return state

# --- View Functions ---

def format_time_str(rem):
    """Formats seconds into MM:SS string."""
    mins, secs = divmod(int(rem), 60)
    return f"{mins:02d}:{secs:02d}"

def standard_view(shared_state, timer_ids):
    """The standard view with settings and controls."""
    st.title("🌐 Server-Wide Shared App")
    st.markdown("Open multiple tabs to see these values sync in real-time.")
    st.header("⏱️ Shared Timers")
    
    col_left, col_right = st.columns(2)

    any_timer_running = False

    for i, tid in enumerate(timer_ids):
        target_col = col_left if i < 2 else col_right

        with target_col:
            rem, total, running, just_finished = shared_state.update_and_get_timer(tid)
            name = shared_state.timers[tid].name
            
            if running:
                any_timer_running = True 
                
            if just_finished:
                st.toast(f"✅ Timer '{name}' has completed and automatically restarted!", icon="🔄")

            with st.container(border=True):
                c1, c2 = st.columns([3, 1]) 
                with c1:
                    st.subheader(f"{name}")
                    time_str = format_time_str(rem)
                    
                    st.metric("Time Remaining", time_str, delta="Running" if running else "Paused")
                    
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
                    
                    if st.button("Restart", key=f"rst_{tid}", use_container_width=True):
                        shared_state.restart_timer(tid)
                        st.rerun()
                        
    # --- Shared Counter & Logs ---
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
            
    return any_timer_running

def full_screen_status_view(shared_state, timer_ids):
    """
    The consolidated view with standard size timer status.
    Uses st.columns(4) for maximum consolidation (single row).
    """
    
    # Custom CSS to hide Streamlit elements in Full Screen Mode
    st.markdown("""
        <style>
        /* Hide the Streamlit header, footer, and main menu */
        header { visibility: hidden; }
        footer { visibility: hidden; }
        .css-1d391kg { padding-top: 0rem; } 
        /* Adjust padding for metrics in the consolidated view */
        .stMetric { padding: 0.5rem !important; }
        .stMetric > div:first-child { font-size: 1rem; }
        .stMetric > div:nth-child(2) > div:first-child { font-size: 1.5rem; }
        </style>
    """, unsafe_allow_html=True)
    
    # Use 4 columns for maximum consolidation (all in one row)
    cols = st.columns(4)
    
    any_timer_running = False

    for i, tid in enumerate(timer_ids):
        target_col = cols[i]

        with target_col:
            rem, total, running, just_finished = shared_state.update_and_get_timer(tid)
            name = shared_state.timers[tid].name
            
            if running:
                any_timer_running = True
                delta_label = "Running"
                delta_color = "normal" 
            else:
                delta_label = "Paused"
                delta_color = "inverse" # Inverse color (red) for paused status
                
            if just_finished:
                st.toast(f"✅ Timer '{name}' has completed and automatically restarted!", icon="🔄")

            time_str = format_time_str(rem)
            
            # Consolidated display using native Streamlit elements (standard size)
            with st.container(border=True):
                st.subheader(f"{name}", divider='gray')
                
                # Use st.metric for the standard size requested
                st.metric(
                    label="Time Remaining",
                    value=time_str,
                    delta=delta_label,
                    delta_color=delta_color
                )

                # Progress Bar
                if total > 0:
                    progress = max(0.0, min(1.0, rem / total))
                else:
                    progress = 0.0
                st.progress(progress)

    return any_timer_running

# 3. Main App Logic
def main():
    # Set initial view mode if not already set
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "Standard View"
        
    # Configure page layout based on view mode
    is_full_screen = st.session_state.view_mode == "Full Screen Status"
    st.set_page_config(page_title="Global Shared Timers", 
                       layout="wide" if is_full_screen else "centered", 
                       initial_sidebar_state="collapsed" if is_full_screen else "auto")
    
    shared_state = get_shared_state_v9()
    timer_ids = ["t1", "t2", "t3", "t4"]

    # --- View Toggle Button (Replaces Sidebar Radio) ---
    if is_full_screen:
        # Show a small button to exit full screen
        if st.button("⬅️ Exit Full Screen Status"):
            st.session_state.view_mode = "Standard View"
            st.rerun()
    else:
        # Show button to enter full screen
        if st.button("➡️ Enter Full Screen Status"):
            st.session_state.view_mode = "Full Screen Status"
            st.rerun()
        
    # --- Render Selected View ---
    if st.session_state.view_mode == "Standard View":
        any_timer_running = standard_view(shared_state, timer_ids)
    else:
        # Full Screen view logic
        any_timer_running = full_screen_status_view(shared_state, timer_ids)
        
    # --- Animation Loop ---
    if any_timer_running:
        # Sleep briefly and rerun to update the progress bar.
        time.sleep(0.1) 
        st.rerun()

if __name__ == "__main__":
    main()

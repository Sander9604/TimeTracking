import streamlit as st
import time

# --- Configuration and Utility Functions ---

# CSS for Full Screen Mode (Large Fonts)
FULL_SCREEN_CSS = """
<style>
/* Target the main metric value (the time remaining) */
div[data-testid="stMetricValue"] {
    font-size: 5.5rem !important; /* Huge font for time */
    font-weight: 900;
    line-height: 1.1;
}
/* Target the metric label (the timer name) */
div[data-testid="stMetricLabel"] {
    font-size: 2.2rem !important; /* Large font for labels */
    font-weight: 500;
    opacity: 0.8;
}
/* Target the progress bar text/label */
.stProgress > div > div > div {
    font-size: 1.5rem !important;
}
/* Center and enlarge the main section header */
h3 {
    text-align: center;
    font-size: 2.5rem !important;
}
</style>
"""

# Function to format total seconds into Minutes:Seconds string
def format_time(seconds):
    """Converts seconds into M:SS format."""
    seconds = max(0, seconds)
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:01d}:{secs:02d}"

# --- State Initialization ---

def initialize_state():
    """Sets up the initial state for the timers using absolute time tracking."""
    
    # 1. Timer Durations (Defaults)
    if 'frame_duration' not in st.session_state:
        st.session_state.frame_duration = 90.0
    if 'twelve_duration' not in st.session_state:
        st.session_state.twelve_duration = 60.0
    
    # 2. Absolute Start Time (Timestamp of when the timer was last reset/started)
    # This is the key for robustness against background pauses.
    if 'frame_start_time' not in st.session_state:
        st.session_state.frame_start_time = time.time()
    if 'twelve_start_time' not in st.session_state:
        st.session_state.twelve_start_time = time.time()
    
    # 3. Cycle Counters (Calculated from start time, but stored for display)
    if 'frame_cycles' not in st.session_state:
        st.session_state.frame_cycles = 0
    if 'twelve_cycles' not in st.session_state:
        st.session_state.twelve_cycles = 0

    # 4. Control Flags
    if 'is_running' not in st.session_state:
        st.session_state.is_running = True # Start running by default
    if 'is_fullscreen' not in st.session_state:
        st.session_state.is_fullscreen = False

def calculate_time_state(timer_key):
    """
    Calculates remaining time, percentage, and cycles completed based on 
    the absolute start time and duration.
    """
    duration = st.session_state[f'{timer_key}_duration']
    start_time = st.session_state[f'{timer_key}_start_time']
    
    if not st.session_state.is_running:
        # When paused, return the state as it was when paused
        cycles = st.session_state[f'{timer_key}_cycles']
        # The stored current time remaining when the pause button was pressed
        # We need to manually store a 'pause offset' for this, or just use the current cycle time
        # For simplicity, we'll store the time remaining at pause, calculated just before the pause button is clicked
        
        # We will use a dedicated state variable to store the 'time-in-cycle' when paused
        time_in_cycle = st.session_state.get(f'{timer_key}_pause_offset', 0)
        remaining_time = duration - time_in_cycle
        percentage = time_in_cycle / duration
        return max(0, remaining_time), percentage, cycles


    # Total time elapsed since the last absolute start time
    elapsed_time = time.time() - start_time
    
    # Calculate time within the current cycle (this handles the looping)
    time_in_cycle = elapsed_time % duration
    
    # Calculate time remaining
    remaining_time = duration - time_in_cycle
    
    # Calculate total cycles completed
    cycles_completed = int(elapsed_time // duration)
    
    # Update session state with the calculated cycle count
    st.session_state[f'{timer_key}_cycles'] = cycles_completed
    
    # Calculate percentage progress for the progress bar
    percentage_completed = time_in_cycle / duration
    
    return max(0, remaining_time), percentage_completed, cycles_completed


# --- Control Functions ---

def reset_timer(timer_key):
    """Resets a single timer's absolute start time and resets its cycle count."""
    st.session_state[f'{timer_key}_start_time'] = time.time()
    st.session_state[f'{timer_key}_cycles'] = 0
    st.session_state[f'{timer_key}_pause_offset'] = 0 # Clear any pause offset
    st.rerun()

def synchronize_timers():
    """Resets both timers to the current absolute time and resets cycle counts."""
    now = time.time()
    st.session_state.frame_start_time = now
    st.session_state.twelve_start_time = now
    st.session_state.frame_cycles = 0
    st.session_state.twelve_cycles = 0
    st.session_state.frame_pause_offset = 0 
    st.session_state.twelve_pause_offset = 0
    st.rerun()

def set_duration_from_inputs(timer_key, minutes, seconds):
    """Updates the timer duration and resets the timer start time."""
    total_seconds = (minutes * 60) + seconds
    if total_seconds > 0:
        st.session_state[f'{timer_key}_duration'] = total_seconds
        # When duration changes, reset the timer to the current absolute time
        reset_timer(timer_key) 
        st.toast(f"{timer_key.capitalize()} Timer duration updated and reset to {format_time(total_seconds)}!")
    else:
        st.warning("Duration must be greater than zero.")

def toggle_run_state():
    """Pauses or Resumes the timer logic by adjusting the start time."""
    
    current_run_state = st.session_state.is_running
    
    if current_run_state:
        # User is PAUSING the timer
        
        # 1. Calculate how far into the cycle we currently are
        frame_time_in_cycle = (time.time() - st.session_state.frame_start_time) % st.session_state.frame_duration
        twelve_time_in_cycle = (time.time() - st.session_state.twelve_start_time) % st.session_state.twelve_duration
        
        # 2. Store this offset time
        st.session_state.frame_pause_offset = frame_time_in_cycle
        st.session_state.twelve_pause_offset = twelve_time_in_cycle
        
        st.session_state.is_running = False # Set pause flag
        st.toast("Countdown Paused.")

    else:
        # User is RESUMING the timer
        
        # 1. Get the stored offset (time elapsed in the cycle when paused)
        frame_offset = st.session_state.frame_pause_offset
        twelve_offset = st.session_state.twelve_pause_offset
        
        # 2. Calculate the NEW start time: Current time minus the time already consumed in the cycle
        st.session_state.frame_start_time = time.time() - frame_offset
        st.session_state.twelve_start_time = time.time() - twelve_offset
        
        st.session_state.is_running = True # Set run flag
        st.session_state.frame_pause_offset = 0 # Clear offsets
        st.session_state.twelve_pause_offset = 0
        st.toast("Countdown Resumed!")
        
    st.rerun()

# --- Main Application Layout ---

st.set_page_config(
    page_title="Absolute Dual Looping Timer", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Infinity Status (Absolute Time Tracking)")

initialize_state()

# Inject Full Screen CSS if enabled
if st.session_state.is_fullscreen:
    st.markdown(FULL_SCREEN_CSS, unsafe_allow_html=True)
    
# --- Input Section (Hidden in Full Screen) ---
if not st.session_state.is_fullscreen:
    st.header("1. Set Timer Durations")
    col_input_1, col_input_2 = st.columns(2)

    # Frame Timer Input
    with col_input_1:
        st.subheader("Frame Timer Duration")
        current_frame_mins = int(st.session_state.frame_duration // 60)
        current_frame_secs = int(st.session_state.frame_duration % 60)

        frame_mins = st.number_input(
            "Minutes (Frame Timer)", 
            min_value=0, 
            value=current_frame_mins, 
            key="input_frame_mins"
        )
        frame_secs = st.number_input(
            "Seconds (Frame Timer)", 
            min_value=0, 
            max_value=59, 
            value=current_frame_secs, 
            key="input_frame_secs"
        )
        if st.button("Set Frame Duration", key="set_frame_duration"):
            set_duration_from_inputs('frame', frame_mins, frame_secs)

    # 12" Timer Input
    with col_input_2:
        st.subheader('12" Timer Duration')
        current_twelve_mins = int(st.session_state.twelve_duration // 60)
        current_twelve_secs = int(st.session_state.twelve_duration % 60)

        twelve_mins = st.number_input(
            "Minutes (12\" Timer)", 
            min_value=0, 
            value=current_twelve_mins, 
            key="input_twelve_mins"
        )
        twelve_secs = st.number_input(
            "Seconds (12\" Timer)", 
            min_value=0, 
            max_value=59, 
            value=current_twelve_secs, 
            key="input_twelve_secs"
        )
        if st.button('Set 12" Duration', key="set_twelve_duration"):
            set_duration_from_inputs('twelve', twelve_mins, twelve_secs)


# --- Control Button Section ---
st.header("2. Timer Controls")

# Always visible controls: Full Screen and Pause/Resume
col_always_visible_1, col_always_visible_2 = st.columns(2)

with col_always_visible_1:
    if st.button("Toggle Full Screen Mode", key="toggle_fullscreen", type="secondary"):
        st.session_state.is_fullscreen = not st.session_state.is_fullscreen
        st.rerun() # Use rerun to apply layout changes immediately

with col_always_visible_2:
    if st.button(f"{'Pause' if st.session_state.is_running else 'Resume'} Countdown", key="toggle_run", type="primary", on_click=toggle_run_state):
        pass # Logic handled in on_click

# Manual Reset Controls (Hidden in Full Screen)
if not st.session_state.is_fullscreen:
    st.markdown("---") # Separator for clarity
    col_controls_1, col_controls_2, col_controls_3 = st.columns(3)

    with col_controls_1:
        st.button("Reset Frame Timer", on_click=lambda: reset_timer('frame'), type="secondary")

    with col_controls_2:
        st.button('Synchronize (Reset Both)', on_click=synchronize_timers, type="secondary")

    with col_controls_3:
        st.button('Reset 12" Timer', on_click=lambda: reset_timer('twelve'), type="secondary")


# --- Display Section ---
st.header("3. Live Countdown")
# Use a larger column ratio in full screen mode for maximum space
if st.session_state.is_fullscreen:
    col_display_1, col_display_2 = st.columns([1, 1])
else:
    col_display_1, col_display_2 = st.columns(2)

# Placeholders for Frame Timer
frame_time_placeholder = col_display_1.empty()
frame_count_placeholder = col_display_1.empty() 
frame_progress_placeholder = col_display_1.empty()

# Placeholders for 12" Timer
twelve_time_placeholder = col_display_2.empty()
twelve_count_placeholder = col_display_2.empty() 
twelve_progress_placeholder = col_display_2.empty()


# --- Main Countdown and Update Loop ---

# Calculate the initial/current state before starting the loop
frame_remaining, frame_percentage, frame_cycles = calculate_time_state('frame')
twelve_remaining, twelve_percentage, twelve_cycles = calculate_time_state('twelve')

# 1. Update Frame Timer UI
frame_progress_placeholder.progress(frame_percentage, text=f"Frame Timer Progress: {format_time(frame_remaining)} remaining")
frame_time_placeholder.metric(
    "Frame Timer",
    format_time(frame_remaining),
    delta_color="off"
)
frame_count_placeholder.metric(
    "Frame Cycles Completed",
    frame_cycles
)

# 2. Update 12" Timer UI
twelve_progress_placeholder.progress(twelve_percentage, text=f'12" Timer Progress: {format_time(twelve_remaining)} remaining')
twelve_time_placeholder.metric(
    '12" Timer',
    format_time(twelve_remaining),
    delta_color="off"
)
twelve_count_placeholder.metric(
    '12" Cycles Completed',
    twelve_cycles
)


if st.session_state.is_running:
    # Use a small sleep to prevent the browser from updating too frequently,
    # but the time calculation remains accurate even if execution is delayed.
    time.sleep(1)
    # The rerun forces the script to execute again, pulling the current time.
    st.rerun()

else:
    st.warning("The countdown is currently paused.")

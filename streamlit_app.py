import streamlit as st
import time

# --- Configuration and Utility Functions ---

# Function to format total seconds into Minutes:Seconds string
def format_time(seconds):
    """Converts seconds into M:SS format."""
    # Ensure seconds is not negative (though it shouldn't be with the reset logic)
    seconds = max(0, seconds)
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:01d}:{secs:02d}"

# --- State Initialization ---

def initialize_state():
    """Sets up the initial state for the timers."""
    if 'frame_duration' not in st.session_state:
        # Default duration: 1 minute 30 seconds
        st.session_state.frame_duration = 90.0
    if 'twelve_duration' not in st.session_state:
        # Default duration: 1 minute 0 seconds
        st.session_state.twelve_duration = 60.0

    # Current remaining time should be initialized to the duration
    if 'frame_current_time' not in st.session_state:
        st.session_state.frame_current_time = st.session_state.frame_duration
    if 'twelve_current_time' not in st.session_state:
        st.session_state.twelve_current_time = st.session_state.twelve_duration
    
    # NEW: Cycle Counters
    if 'frame_reset_count' not in st.session_state:
        st.session_state.frame_reset_count = 0
    if 'twelve_reset_count' not in st.session_state:
        st.session_state.twelve_reset_count = 0

    # Flag to pause/unpause the entire system
    if 'is_running' not in st.session_state:
        st.session_state.is_running = True

# --- Control Functions ---

def reset_timer(timer_key):
    """Resets a single timer to its initial duration and resets its cycle count."""
    duration_key = f'{timer_key}_duration'
    current_key = f'{timer_key}_current_time'
    count_key = f'{timer_key}_reset_count'
    
    if duration_key in st.session_state and current_key in st.session_state:
        st.session_state[current_key] = st.session_state[duration_key]
        st.session_state[count_key] = 0 # Reset the count on manual button press

def synchronize_timers():
    """Resets both timers to their initial durations and cycle counts."""
    reset_timer('frame')
    reset_timer('twelve')

def set_duration_from_inputs(timer_key, minutes, seconds):
    """Updates the timer duration, resets its current time, and resets cycle count."""
    total_seconds = (minutes * 60) + seconds
    if total_seconds > 0:
        duration_key = f'{timer_key}_duration'
        st.session_state[duration_key] = total_seconds
        # Reset the current timer and count to the new duration
        reset_timer(timer_key)
    else:
        st.warning("Duration must be greater than zero.")

# --- Main Application Layout ---

st.set_page_config(
    page_title="Dual Looping Timer", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Infinity Status")

initialize_state()

# --- Input Section ---
st.header("1. Set Timer Durations")
col_input_1, col_input_2 = st.columns(2)

# Frame Timer Input
with col_input_1:
    st.subheader("Frame Timer Duration")
    # Calculate current min/sec for display in input fields
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
        st.success(f"Frame Timer set to {format_time(st.session_state.frame_duration)}")

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
        st.success(f'12" Timer set to {format_time(st.session_state.twelve_duration)}')


# --- Control Button Section ---
st.header("2. Timer Controls")
col_controls_1, col_controls_2, col_controls_3 = st.columns(3)

with col_controls_1:
    st.button("Reset Frame Timer", on_click=lambda: reset_timer('frame'), type="secondary")

with col_controls_2:
    st.button('Synchronize (Reset Both)', on_click=synchronize_timers, type="primary")

with col_controls_3:
    st.button('Reset 12" Timer', on_click=lambda: reset_timer('twelve'), type="secondary")

# Pause/Resume Button
if st.button("Pause/Resume Countdown", key="toggle_run"):
    st.session_state.is_running = not st.session_state.is_running
    if st.session_state.is_running:
        st.toast("Countdown Resumed!")
    else:
        st.toast("Countdown Paused.")

# --- Display Section ---
st.header("3. Live Countdown")
# Create placeholders for the dynamic display
col_display_1, col_display_2 = st.columns(2)

# Placeholders for Frame Timer
frame_time_placeholder = col_display_1.empty()
frame_count_placeholder = col_display_1.empty() # Placeholder for the new cycle count
frame_progress_placeholder = col_display_1.empty()

# Placeholders for 12" Timer
twelve_time_placeholder = col_display_2.empty()
twelve_count_placeholder = col_display_2.empty() # Placeholder for the new cycle count
twelve_progress_placeholder = col_display_2.empty()


# --- Main Countdown Loop ---

if st.session_state.is_running:
    while True:
        # Calculate Time Remaining
        frame_time = st.session_state.frame_current_time
        twelve_time = st.session_state.twelve_current_time

        # --- Update Frame Timer ---
        frame_percentage = 1.0 - (frame_time / st.session_state.frame_duration)
        frame_progress_placeholder.progress(frame_percentage, text=f"Frame Timer Progress: {format_time(frame_time)} remaining")
        
        frame_time_placeholder.metric(
            "Frame Timer (Resets at 0)",
            format_time(frame_time),
            delta_color="off"
        )
        # Display the cycle count
        frame_count_placeholder.metric(
            "Frame Cycles Completed",
            st.session_state.frame_reset_count
        )
        
        # --- Update 12" Timer ---
        twelve_percentage = 1.0 - (twelve_time / st.session_state.twelve_duration)
        twelve_progress_placeholder.progress(twelve_percentage, text=f'12" Timer Progress: {format_time(twelve_time)} remaining')

        twelve_time_placeholder.metric(
            '12" Timer (Resets at 0)',
            format_time(twelve_time),
            delta_color="off"
        )
        # Display the cycle count
        twelve_count_placeholder.metric(
            '12" Cycles Completed',
            st.session_state.twelve_reset_count
        )

        # 1. Decrement Time
        st.session_state.frame_current_time -= 1
        st.session_state.twelve_current_time -= 1

        # 2. Check for Reset (Looping behavior)
        if st.session_state.frame_current_time < 0:
            st.session_state.frame_current_time = st.session_state.frame_duration - 1
            st.session_state.frame_reset_count += 1 # INCREMENT COUNTER
            st.toast("Frame Timer cycle complete! Restarting.")

        if st.session_state.twelve_current_time < 0:
            st.session_state.twelve_current_time = st.session_state.twelve_duration - 1
            st.session_state.twelve_reset_count += 1 # INCREMENT COUNTER
            st.toast('12" Timer cycle complete! Restarting.')

        # 3. Wait for 1 second before the next update
        time.sleep(1)

else:
    # Display final metrics when paused
    frame_time_placeholder.metric("Frame Timer (PAUSED)", format_time(st.session_state.frame_current_time))
    frame_count_placeholder.metric("Frame Cycles Completed", st.session_state.frame_reset_count)
    frame_progress_placeholder.progress(1.0 - (st.session_state.frame_current_time / st.session_state.frame_duration), text="Countdown Paused")

    twelve_time_placeholder.metric('12" Timer (PAUSED)', format_time(st.session_state.twelve_current_time))
    twelve_count_placeholder.metric('12" Cycles Completed', st.session_state.twelve_reset_count)
    twelve_progress_placeholder.progress(1.0 - (st.session_state.twelve_current_time / st.session_state.twelve_duration), text="Countdown Paused")

    st.warning("The countdown is currently paused.")

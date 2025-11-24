<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infinity Status</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
            transition: background-color 0.3s;
        }
        /* Custom styles for large metrics in fullscreen mode */
        .fullscreen-mode .metric-value {
            font-size: 8rem;
            font-weight: 900;
            line-height: 1;
        }
        .fullscreen-mode .metric-label {
            font-size: 2.5rem;
            font-weight: 700;
            color: #58a6ff;
            margin-bottom: 1rem;
        }
        .fullscreen-mode .cycle-count {
            font-size: 4rem;
            font-weight: 800;
            color: #79c0ff;
        }
        .metric-card {
            background-color: #161b22;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
            border: 1px solid #30363d;
        }
        .progress-bar {
            height: 1rem;
        }
        .progress-fill-frame {
            background-color: #2fb92f; /* Green */
        }
        .progress-fill-twelve {
            background-color: #58a6ff; /* Blue */
        }
    </style>
</head>
<body class="p-4 md:p-8" id="app-body">

    <div id="loading-indicator" class="text-center py-20 text-xl text-gray-400">
        Loading synchronized state...
    </div>

    <div id="app-container" class="hidden">
        <h1 class="text-4xl font-bold text-center mb-6 text-blue-400">Infinity Status</h1>
        
        <!-- Controls & Settings (Visible when not in Full Screen) -->
        <div id="settings-section" class="mb-8 p-4 bg-gray-800/50 rounded-xl shadow-lg border border-gray-700/50">
            <h2 class="text-2xl font-semibold mb-4 border-b border-gray-700 pb-2">1. Set Timer Durations</h2>
            <div class="grid md:grid-cols-2 gap-6">
                <!-- Frame Timer Input -->
                <div class="p-4 bg-gray-700/50 rounded-lg">
                    <h3 class="text-xl font-medium mb-3">Frame Timer</h3>
                    <div class="flex space-x-2 mb-3">
                        <input type="number" id="frame-mins-input" min="0" class="w-1/2 p-2 rounded-lg bg-gray-900 border border-gray-600 focus:ring-blue-500 focus:border-blue-500 text-white" placeholder="Minutes" value="1">
                        <input type="number" id="frame-secs-input" min="0" max="59" class="w-1/2 p-2 rounded-lg bg-gray-900 border border-gray-600 focus:ring-blue-500 focus:border-blue-500 text-white" placeholder="Seconds" value="30">
                    </div>
                    <button id="set-frame-btn" class="w-full py-2 bg-green-600 hover:bg-green-700 rounded-lg font-bold transition">Set Frame Duration</button>
                </div>

                <!-- 12" Timer Input -->
                <div class="p-4 bg-gray-700/50 rounded-lg">
                    <h3 class="text-xl font-medium mb-3">12" Timer</h3>
                    <div class="flex space-x-2 mb-3">
                        <input type="number" id="twelve-mins-input" min="0" class="w-1/2 p-2 rounded-lg bg-gray-900 border border-gray-600 focus:ring-blue-500 focus:border-blue-500 text-white" placeholder="Minutes" value="1">
                        <input type="number" id="twelve-secs-input" min="0" max="59" class="w-1/2 p-2 rounded-lg bg-gray-900 border border-gray-600 focus:ring-blue-500 focus:border-blue-500 text-white" placeholder="Seconds" value="0">
                    </div>
                    <button id="set-twelve-btn" class="w-full py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-bold transition">Set 12" Duration</button>
                </div>
            </div>
        </div>
        
        <!-- Controls (Always Visible) -->
        <div class="mb-6 p-4 bg-gray-800/50 rounded-xl shadow-lg border border-gray-700/50">
            <h2 class="text-2xl font-semibold mb-4 border-b border-gray-700 pb-2">2. Controls</h2>
            <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
                <button id="sync-btn" class="col-span-2 md:col-span-1 py-3 bg-indigo-600 hover:bg-indigo-700 rounded-xl font-bold transition">Synchronize (Reset Both)</button>
                <button id="reset-frame-btn" class="col-span-1 py-3 bg-gray-600 hover:bg-gray-700 rounded-xl font-bold transition">Reset Frame</button>
                <button id="reset-twelve-btn" class="col-span-1 py-3 bg-gray-600 hover:bg-gray-700 rounded-xl font-bold transition">Reset 12"</button>
                
                <button id="toggle-fullscreen-btn" class="col-span-2 md:col-span-1 py-3 bg-yellow-600 hover:bg-yellow-700 rounded-xl font-bold transition flex items-center justify-center">
                    <svg id="fullscreen-icon" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4M4 20l5-5m11 5v-4m0 4h-4m4 0l-5-5"></path></svg>
                    Toggle Full Screen
                </button>
            </div>
        </div>

        <!-- Live Display Section -->
        <h2 id="display-header" class="text-2xl font-semibold mb-4 border-b border-gray-700 pb-2">3. Live Status (Synchronized)</h2>
        <div class="grid md:grid-cols-2 gap-8">
            <!-- Frame Timer Display -->
            <div id="frame-card" class="metric-card p-6 rounded-xl transition">
                <div class="flex justify-between items-start mb-4">
                    <div class="metric-label text-xl font-semibold text-green-400">Frame Timer (Resets at 0)</div>
                    <div class="cycle-count text-2xl font-bold text-green-300" id="frame-cycles">0</div>
                </div>
                <div class="metric-value text-6xl font-extrabold text-white mb-4" id="frame-time">0:00</div>
                <div class="progress-bar w-full bg-gray-700 rounded-full">
                    <div id="frame-progress" class="progress-fill-frame h-full rounded-full transition-all duration-100 ease-linear" style="width: 0%;"></div>
                </div>
                <p id="frame-progress-text" class="text-sm mt-2 text-gray-400">Time remaining: 0:00</p>
            </div>

            <!-- 12" Timer Display -->
            <div id="twelve-card" class="metric-card p-6 rounded-xl transition">
                <div class="flex justify-between items-start mb-4">
                    <div class="metric-label text-xl font-semibold text-blue-400">12" Timer (Resets at 0)</div>
                    <div class="cycle-count text-2xl font-bold text-blue-300" id="twelve-cycles">0</div>
                </div>
                <div class="metric-value text-6xl font-extrabold text-white mb-4" id="twelve-time">0:00</div>
                <div class="progress-bar w-full bg-gray-700 rounded-full">
                    <div id="twelve-progress" class="progress-fill-twelve h-full rounded-full transition-all duration-100 ease-linear" style="width: 0%;"></div>
                </div>
                <p id="twelve-progress-text" class="text-sm mt-2 text-gray-400">Time remaining: 0:00</p>
            </div>
        </div>
        
        <div id="user-info" class="text-sm text-gray-500 mt-8 text-center">
            User ID: <span id="current-user-id">...</span>
        </div>
    </div>

    <!-- Firebase SDKs -->
    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
        import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
        import { getFirestore, doc, setDoc, onSnapshot, updateDoc } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";
        // import { setLogLevel } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";
        
        // setLogLevel('Debug'); // Uncomment for debugging Firestore logs

        // --- GLOBAL CONFIGS (Provided by the environment) ---
        const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
        const firebaseConfig = JSON.parse(typeof __firebase_config !== 'undefined' ? __firebase_config : '{}');
        const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;
        const TIMER_DOC_PATH = `artifacts/${appId}/public/data/timers/timer_state`;
        
        let db;
        let auth;
        let userId = 'anonymous'; // Will be updated on sign-in
        let isAuthReady = false;
        
        // Timer state defaults
        const DEFAULT_DURATIONS = {
            frame: 90.0,
            twelve: 60.0
        };

        // Local state copy
        let synchronizedState = {
            frame_duration: DEFAULT_DURATIONS.frame,
            twelve_duration: DEFAULT_DURATIONS.twelve,
            frame_start_time: Date.now(),
            twelve_start_time: Date.now(),
            frame_cycles: 0,
            twelve_cycles: 0
        };
        
        let intervalId = null;
        let isPaused = false;
        let isFullscreen = false;


        // --- UI UTILITIES ---

        function formatTime(seconds) {
            seconds = Math.max(0, Math.floor(seconds));
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
        }

        function toggleFullscreen() {
            isFullscreen = !isFullscreen;
            const body = document.getElementById('app-body');
            const settingsSection = document.getElementById('settings-section');
            const displayHeader = document.getElementById('display-header');

            if (isFullscreen) {
                body.classList.add('fullscreen-mode');
                settingsSection.classList.add('hidden');
                displayHeader.classList.add('hidden');
            } else {
                body.classList.remove('fullscreen-mode');
                settingsSection.classList.remove('hidden');
                displayHeader.classList.remove('hidden');
            }
        }
        
        // --- FIREBASE INITIALIZATION & AUTH ---

        async function initializeFirebase() {
            try {
                const app = initializeApp(firebaseConfig);
                auth = getAuth(app);
                db = getFirestore(app);

                // 1. Authenticate
                if (initialAuthToken) {
                    await signInWithCustomToken(auth, initialAuthToken);
                } else {
                    await signInAnonymously(auth);
                }

                // 2. Set up Auth Listener
                onAuthStateChanged(auth, (user) => {
                    if (user) {
                        userId = user.uid;
                        document.getElementById('current-user-id').textContent = userId;
                        isAuthReady = true;
                        startRealTimeListener();
                        document.getElementById('loading-indicator').classList.add('hidden');
                        document.getElementById('app-container').classList.remove('hidden');
                    } else {
                        console.error("Authentication failed.");
                    }
                });

            } catch (error) {
                console.error("Error initializing Firebase:", error);
                document.getElementById('loading-indicator').textContent = 'Error loading application. Check console for details.';
            }
        }

        // --- FIREBASE DATA OPERATIONS ---

        // Function to update the database when a reset/synchronization occurs
        async function updateTimerState(timerKey, duration, cycles, newStartTime) {
            if (!isAuthReady) return console.error("Auth not ready for update.");

            const docRef = doc(db, TIMER_DOC_PATH);
            const updateData = {
                [`${timerKey}_duration`]: duration,
                [`${timerKey}_start_time`]: newStartTime,
                [`${timerKey}_cycles`]: cycles,
            };

            try {
                await updateDoc(docRef, updateData);
                // The onSnapshot listener will update all clients, including this one.
            } catch (e) {
                // If the document doesn't exist, create it (should only happen on first run)
                if (e.code === 'not-found') {
                    await setDoc(docRef, { ...synchronizedState, [`${timerKey}_start_time`]: newStartTime });
                } else {
                    console.error("Error updating timer state:", e);
                }
            }
        }
        
        // Function to update *both* timers (for the Synchronize button)
        async function updateBothTimers(newStartTime) {
             if (!isAuthReady) return console.error("Auth not ready for update.");

            const docRef = doc(db, TIMER_DOC_PATH);
            const updateData = {
                frame_duration: synchronizedState.frame_duration,
                twelve_duration: synchronizedState.twelve_duration,
                frame_start_time: newStartTime,
                twelve_start_time: newStartTime,
                frame_cycles: 0,
                twelve_cycles: 0,
            };

            try {
                await setDoc(docRef, updateData); // Use setDoc to ensure existence and full overwrite
            } catch (e) {
                console.error("Error synchronizing timers:", e);
            }
        }

        // --- REAL-TIME LISTENER ---

        function startRealTimeListener() {
            if (!isAuthReady) return;

            const docRef = doc(db, TIMER_DOC_PATH);

            onSnapshot(docRef, (docSnapshot) => {
                if (docSnapshot.exists()) {
                    // Update local state copy with synchronized server data
                    const data = docSnapshot.data();
                    synchronizedState = {
                        frame_duration: data.frame_duration || DEFAULT_DURATIONS.frame,
                        twelve_duration: data.twelve_duration || DEFAULT_DURATIONS.twelve,
                        frame_start_time: data.frame_start_time || Date.now(),
                        twelve_start_time: data.twelve_start_time || Date.now(),
                        frame_cycles: data.frame_cycles || 0,
                        twelve_cycles: data.twelve_cycles || 0
                    };
                    
                    // Update duration inputs to reflect the latest state from Firestore
                    document.getElementById('frame-mins-input').value = Math.floor(synchronizedState.frame_duration / 60);
                    document.getElementById('frame-secs-input').value = Math.floor(synchronizedState.frame_duration % 60);
                    document.getElementById('twelve-mins-input').value = Math.floor(synchronizedState.twelve_duration / 60);
                    document.getElementById('twelve-secs-input').value = Math.floor(synchronizedState.twelve_duration % 60);

                    // Re-start the display loop to immediately reflect the new state
                    if (intervalId) clearInterval(intervalId);
                    intervalId = setInterval(updateDisplay, 50); // Update display frequently for smooth progress bar
                    
                } else {
                    // Document doesn't exist (first run), initialize with default values
                    const initialData = {
                        frame_duration: DEFAULT_DURATIONS.frame,
                        twelve_duration: DEFAULT_DURATIONS.twelve,
                        frame_start_time: Date.now(),
                        twelve_start_time: Date.now(),
                        frame_cycles: 0,
                        twelve_cycles: 0
                    };
                    setDoc(docRef, initialData).catch(e => console.error("Error setting initial doc:", e));
                }
            }, (error) => {
                console.error("Real-time listener failed:", error);
            });
        }
        
        // --- DISPLAY & LOGIC LOOP ---

        function updateDisplay() {
            if (isPaused) return;

            const currentTime = Date.now();
            
            // --- FRAME TIMER CALCULATION ---
            let elapsedFrame = (currentTime - synchronizedState.frame_start_time) / 1000;
            let remainingFrame = synchronizedState.frame_duration - (elapsedFrame % synchronizedState.frame_duration);
            let frameProgress = 100 * (1 - (remainingFrame / synchronizedState.frame_duration));
            
            // Check for Frame Timer completion (and potential asynchronous reset)
            if (remainingFrame <= 0) {
                // Determine how many cycles were completed since the last check
                const cyclesCompleted = Math.floor(elapsedFrame / synchronizedState.frame_duration);
                if (cyclesCompleted > 0) {
                    const newStartTime = currentTime - ((elapsedFrame % synchronizedState.frame_duration) * 1000);
                    const newCycles = synchronizedState.frame_cycles + cyclesCompleted;
                    
                    // Update Firestore with the new synchronized start time and cycle count
                    updateTimerState('frame', synchronizedState.frame_duration, newCycles, newStartTime);
                    // No need to update local state, onSnapshot handles it.
                    return; // Stop local update, wait for Firestore update
                }
            }
            
            // --- 12" TIMER CALCULATION ---
            let elapsedTwelve = (currentTime - synchronizedState.twelve_start_time) / 1000;
            let remainingTwelve = synchronizedState.twelve_duration - (elapsedTwelve % synchronizedState.twelve_duration);
            let twelveProgress = 100 * (1 - (remainingTwelve / synchronizedState.twelve_duration));
            
            // Check for 12" Timer completion
            if (remainingTwelve <= 0) {
                const cyclesCompleted = Math.floor(elapsedTwelve / synchronizedState.twelve_duration);
                 if (cyclesCompleted > 0) {
                    const newStartTime = currentTime - ((elapsedTwelve % synchronizedState.twelve_duration) * 1000);
                    const newCycles = synchronizedState.twelve_cycles + cyclesCompleted;
                    
                    // Update Firestore with the new synchronized start time and cycle count
                    updateTimerState('twelve', synchronizedState.twelve_duration, newCycles, newStartTime);
                    // No need to update local state, onSnapshot handles it.
                    return; // Stop local update, wait for Firestore update
                }
            }
            
            // --- UI RENDER ---
            
            // Frame UI
            document.getElementById('frame-time').textContent = formatTime(remainingFrame);
            document.getElementById('frame-progress').style.width = `${Math.min(100, frameProgress)}%`;
            document.getElementById('frame-progress-text').textContent = `Time remaining: ${formatTime(remainingFrame)}`;
            document.getElementById('frame-cycles').textContent = synchronizedState.frame_cycles;

            // 12" UI
            document.getElementById('twelve-time').textContent = formatTime(remainingTwelve);
            document.getElementById('twelve-progress').style.width = `${Math.min(100, twelveProgress)}%`;
            document.getElementById('twelve-progress-text').textContent = `Time remaining: ${formatTime(remainingTwelve)}`;
            document.getElementById('twelve-cycles').textContent = synchronizedState.twelve_cycles;
        }

        // --- BUTTON HANDLERS ---
        
        // Reset a single timer (manual reset)
        document.getElementById('reset-frame-btn').addEventListener('click', () => {
            if (!isAuthReady) return;
            // Set the start time to the current moment, reset cycles to 0
            updateTimerState('frame', synchronizedState.frame_duration, 0, Date.now());
        });

        document.getElementById('reset-twelve-btn').addEventListener('click', () => {
            if (!isAuthReady) return;
            // Set the start time to the current moment, reset cycles to 0
            updateTimerState('twelve', synchronizedState.twelve_duration, 0, Date.now());
        });

        // Synchronize (Reset Both)
        document.getElementById('sync-btn').addEventListener('click', () => {
            if (!isAuthReady) return;
            // Set both start times to the current moment, reset cycles to 0
            updateBothTimers(Date.now());
        });

        // Set Duration
        document.getElementById('set-frame-btn').addEventListener('click', () => {
            if (!isAuthReady) return;
            const mins = parseInt(document.getElementById('frame-mins-input').value) || 0;
            const secs = parseInt(document.getElementById('frame-secs-input').value) || 0;
            const newDuration = (mins * 60) + secs;
            if (newDuration <= 0) return alert("Duration must be greater than zero.");
            
            // When duration changes, update duration in state and reset the timer start time and cycles
            updateTimerState('frame', newDuration, 0, Date.now());
        });

        document.getElementById('set-twelve-btn').addEventListener('click', () => {
            if (!isAuthReady) return;
            const mins = parseInt(document.getElementById('twelve-mins-input').value) || 0;
            const secs = parseInt(document.getElementById('twelve-secs-input').value) || 0;
            const newDuration = (mins * 60) + secs;
            if (newDuration <= 0) return alert("Duration must be greater than zero.");

            // When duration changes, update duration in state and reset the timer start time and cycles
            updateTimerState('twelve', newDuration, 0, Date.now());
        });
        
        // Full Screen Toggle
        document.getElementById('toggle-fullscreen-btn').addEventListener('click', toggleFullscreen);


        // --- START APP ---
        window.onload = initializeFirebase;

    </script>
</body>
</html>

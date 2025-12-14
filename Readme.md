# 💻 SAM-CPU-SIM (System Assistant Mate - CPU Simulator)

SAM-CPU-SIM is a lightweight, cross-platform CPU usage pet simulator designed to run as an always-on-top desktop overlay. It uses a Rust backend for efficient CPU metric calculations and a Python frontend (with Pygame) for the visual pet and interaction logic.

## 🚀 Key Features

* **Desktop Overlay:** Runs seamlessly on top of other applications (Windows support via `win32gui`).
* **Rust Core:** Utilizes Rust for performance-critical CPU simulation and metrics via the `rust_core` module.
* **Emotional Pet:** The pet, Clippy, reacts to system metrics (CPU Temperature, Power, etc.) with spoken text-to-speech feedback using `edge-tts`.
* **Interactive Menu:** A control menu to adjust themes and monitor detailed metrics (Right-click to open).

## ⚙️ Prerequisites

You must have the following software installed on your system to **build** and **run** the application.

1.  **Python:** Version 3.10 or higher.
2.  **Rust:** The Rust toolchain (including `cargo`) must be installed. Install it via [rustup](https://www.rust-lang.org/tools/install).
3.  **Maturin:** The essential tool used to build the Python-Rust bridge.

## 🛠️ Setup and Installation

Follow these steps to set up the environment and build the necessary components.

### 1. Clone the Repository
```bash 
cd SAM-CPU-SIM/CPU_PET_SIM/
```

### 2. Set up the Python Virtual Environment
```bash 
python -m venv venv
```

```bash
.\venv\Scripts\Activate
```

### 4. Build the Rust Backend (rust_core)
```bash 
maturin develop
```

## Running the Application
```bash
python python_app/main.py
```


### Troubleshooting Common Issues
* Since your application mixes the synchronous Pygame loop with the asynchronous Text-to-Speech library (edge-tts), specific concurrency errors are common.

# Issue 1: RuntimeError: asyncio.run() cannot be called from a running event loop
* This crash occurs because the Pygame main loop is synchronous, but the edge-tts calls (inside Clippy_Personality.py) are asynchronous and use asyncio.run(), which is illegal to call repeatedly in a single thread.

#### The Fix:

* The current code is designed to resolve this by isolating the speech generation into a separate, independent thread. This is handled by a wrapper function (_run_speak_async_in_thread) and threading.Thread calls in Clippy_Personality.py.

* If you see this error, ensure you have the _run_speak_async_in_thread function defined outside the Personality class, and that say_for_mood and say_random_idle use threading.Thread to execute it.

# Issue 2: ImportError: cannot import name 'CPU' from 'rust_core'
This means the Rust module was not built or installed correctly into the Python environment.

### The Fix:

* Ensure your virtual environment is active (.\venv\Scripts\Activate).

* Navigate to the directory containing your Cargo.toml.

* Re-run: maturin develop.

### Issue 3: AttributeError: 'ControlMenu' object has no attribute 'close'
This crash occurs when you right-click to close the control menu.


```code in main.py 
line 66 - 80

def close_control_menu():
    global menu, menu_open
    if menu_open:
        print("Control menu Closed")
        # menu.close() # <-- THIS LINE MUST BE REMOVED/COMMENTED OUT
        menu = None
        menu_open = False
```


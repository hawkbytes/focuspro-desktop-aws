import os
import sys
import time
import threading
import subprocess
import requests
import logging
import tkinter as tk
import webview
import psutil
import webbrowser
import pathlib
import signal
import atexit

# System tray imports
try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    logging.warning("pystray or PIL not available - system tray icon disabled")

# Fix working directory for double-click launches
def fix_working_directory():
    """Ensure we're in the correct working directory"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        if sys.platform == 'darwin':  # macOS
            # Get the app bundle's Resources directory or the parent directory
            app_path = os.path.dirname(sys.executable)
            if 'Contents/MacOS' in app_path:
                # We're inside an app bundle, go to the project root
                project_root = os.path.join(app_path, '..', '..', '..', '..')
                project_root = os.path.abspath(project_root)
                if os.path.exists(os.path.join(project_root, 'app.py')):
                    os.chdir(project_root)
                    print(f"[INIT] Set working directory to project root: {project_root}")
                else:
                    # Try the MacOS directory itself
                    os.chdir(app_path)
                    print(f"[INIT] Set working directory to app path: {app_path}")
            else:
                os.chdir(app_path)
                print(f"[INIT] Set working directory to: {app_path}")
        else:
            # Windows/Linux
            app_dir = os.path.dirname(sys.executable)
            os.chdir(app_dir)
            print(f"[INIT] Set working directory to: {app_dir}")
    else:
        # Running as script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        print(f"[INIT] Set working directory to script location: {script_dir}")

# Fix working directory first
fix_working_directory()

# Create necessary folders on startup
def create_required_folders():
    folders_to_create = ["logs", "output", "data"]
    for folder in folders_to_create:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            print(f"[OK] Created folder: {folder}")

# Call folder creation
create_required_folders()

def open_exec_terminal():
    """Opens the exec terminal automatically (DISABLED for silent operation)"""
    try:
        # Get the directory where the desktop app is located
        base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
        
        logging.info(f"[EXEC] Terminal opening disabled for silent operation from: {base_path}")
        
        # DISABLED: Don't open terminal window for silent GUI operation
        # This prevents the command prompt from appearing when starting the GUI
        logging.info("[INFO] Silent mode: Terminal opening disabled")
        
        # No sleep needed since we're not opening anything
        
    except Exception as e:
        logging.warning(f"[WARN] Error in terminal function: {e}")
        logging.info("[INFO] Continuing silently...")

def kill_existing_connector():
    """Kill any existing DDSFocusPro processes"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower()
                cmdline_str = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                
                # Check for various DDSFocusPro process patterns
                should_kill = (
                    'connector.exe' in proc_name or
                    ('python.exe' in proc_name and 'app.py' in cmdline_str) or
                    ('python' in proc_name and ('app.py' in cmdline_str or 'DDSFocusPro' in cmdline_str))
                )
                
                if should_kill:
                    logging.info(f"[CLEAN] Killing existing process: PID {proc.pid} - {proc_name}")
                    try:
                        proc.terminate()
                        proc.wait(timeout=3)
                    except (psutil.TimeoutExpired, psutil.AccessDenied):
                        try:
                            proc.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    except psutil.NoSuchProcess:
                        pass  # Process already gone
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                logging.warning(f"[WARN] Could not check/kill process {proc.info.get('pid', 'unknown')}: {e}")
                continue
                
    except Exception as e:
        logging.warning(f"[WARN] Error during existing process cleanup: {e}")

# ------------------ Globals ------------------
connector_process = None
flask_ready = False
cleanup_in_progress = False
flask_pids = set()  # Track all Flask process PIDs
pid_file = "ddsfocus_pids.txt"  # File to persist PIDs
tray_icon = None  # System tray icon instance
tray_thread = None  # Thread running the tray icon
window_should_exit = False  # Flag to control if window close should exit app
window_hidden = False  # Track if window is currently hidden

# ------------------ System Tray Functions ------------------
def create_tray_icon():
    """Create and display system tray icon"""
    global tray_icon
    
    if not TRAY_AVAILABLE:
        logging.warning("[TRAY] System tray not available (pystray/PIL not installed)")
        return None
    
    try:
        # Try to load the app icon - prefer ICO for Windows
        base_paths = [
            os.getcwd(),
            os.path.dirname(__file__),
            os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd(),
        ]
        
        icon_files = ["icon.ico", "favicon.ico", "dds-logo.png", "dds-logo.ico", "icon.png"]
        
        icon_image = None
        for base in base_paths:
            for icon_file in icon_files:
                icon_path = os.path.join(base, "static", icon_file)
                if os.path.exists(icon_path):
                    try:
                        icon_image = Image.open(icon_path)
                        # Convert to RGBA for proper transparency
                        if icon_image.mode != 'RGBA':
                            icon_image = icon_image.convert('RGBA')
                        # Resize to standard Windows tray icon size (16x16 or 32x32)
                        icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
                        logging.info(f"[TRAY] Loaded icon from: {icon_path}")
                        break
                    except Exception as e:
                        logging.warning(f"[TRAY] Could not load icon {icon_path}: {e}")
                        continue
            if icon_image:
                break
        
        # If no icon found, create a simple colored icon with DDS branding
        if icon_image is None:
            logging.info("[TRAY] Creating default DDS icon")
            # Create a green circle icon
            icon_image = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
            from PIL import ImageDraw
            draw = ImageDraw.Draw(icon_image)
            # Draw filled green circle
            draw.ellipse([2, 2, 30, 30], fill=(0, 96, 57, 255), outline=(255, 255, 255, 255))
            # Draw "D" letter in center
            try:
                draw.text((10, 6), "D", fill=(255, 255, 255, 255))
            except:
                pass  # If font fails, just use the circle
        
        def show_window(icon, item):
            """Show/focus the main window"""
            global window_hidden
            try:
                if webview.windows:
                    webview.windows[0].show()
                    # Try to restore and bring to front
                    try:
                        webview.windows[0].restore()
                    except:
                        pass
                    window_hidden = False
                    logging.info("[TRAY] Window shown and restored")
            except Exception as e:
                logging.warning(f"[TRAY] Could not show window: {e}")
        
        def hide_window(icon, item):
            """Hide the main window to system tray"""
            global window_hidden
            try:
                if webview.windows:
                    webview.windows[0].hide()
                    window_hidden = True
                    logging.info("[TRAY] Window hidden to tray")
            except Exception as e:
                logging.warning(f"[TRAY] Could not hide window: {e}")
        
        def open_browser(icon, item):
            """Open the app in browser"""
            try:
                ports = [5000, 5001, 5002, 5003, 5004, 5005]
                for port in ports:
                    try:
                        r = requests.get(f"http://127.0.0.1:{port}", timeout=1)
                        if r.status_code == 200:
                            webbrowser.open(f"http://127.0.0.1:{port}")
                            logging.info(f"[TRAY] Opened browser at port {port}")
                            return
                    except:
                        continue
            except Exception as e:
                logging.warning(f"[TRAY] Could not open browser: {e}")
        
        def exit_app(icon, item):
            """Exit the application"""
            global window_should_exit
            logging.info("[TRAY] Exit requested from tray")
            window_should_exit = True
            # Stop tray icon first
            try:
                icon.stop()
            except:
                pass
            # Then cleanup and exit
            cleanup_and_exit()
        
        # Create tray menu
        menu = Menu(
            MenuItem("Show DDS FocusPro", show_window, default=True),
            MenuItem("Hide to Tray", hide_window),
            MenuItem("Open in Browser", open_browser),
            Menu.SEPARATOR,
            MenuItem("Exit", exit_app)
        )
        
        # Create the tray icon
        tray_icon = Icon(
            name="DDSFocusPro",
            icon=icon_image,
            title="DDS FocusPro - Time Tracker",
            menu=menu
        )
        
        logging.info("[TRAY] System tray icon created")
        return tray_icon
        
    except Exception as e:
        logging.error(f"[TRAY] Failed to create tray icon: {e}")
        return None

def run_tray_icon():
    """Run the system tray icon in a separate thread"""
    global tray_icon
    
    if not TRAY_AVAILABLE:
        return
    
    try:
        tray_icon = create_tray_icon()
        if tray_icon:
            logging.info("[TRAY] Starting system tray icon...")
            tray_icon.run()
    except Exception as e:
        logging.error(f"[TRAY] Error running tray icon: {e}")

def stop_tray_icon():
    """Stop the system tray icon"""
    global tray_icon
    
    try:
        if tray_icon:
            tray_icon.stop()
            logging.info("[TRAY] System tray icon stopped")
    except Exception as e:
        logging.warning(f"[TRAY] Error stopping tray icon: {e}")

def save_pid(pid):
    """Save a PID to the tracking file"""
    try:
        flask_pids.add(pid)
        with open(pid_file, 'w') as f:
            for saved_pid in flask_pids:
                f.write(f"{saved_pid}\n")
        logging.info(f" Saved PID {pid} to tracking file")
    except Exception as e:
        logging.warning(f" Could not save PID {pid}: {e}")

def load_pids():
    """Load PIDs from the tracking file"""
    try:
        if os.path.exists(pid_file):
            with open(pid_file, 'r') as f:
                for line in f:
                    pid = int(line.strip())
                    flask_pids.add(pid)
            logging.info(f" Loaded {len(flask_pids)} PIDs from tracking file")
    except Exception as e:
        logging.warning(f" Could not load PIDs: {e}")

def remove_pid(pid):
    """Remove a PID from tracking"""
    try:
        flask_pids.discard(pid)
        with open(pid_file, 'w') as f:
            for saved_pid in flask_pids:
                f.write(f"{saved_pid}\n")
        logging.info(f" Removed PID {pid} from tracking")
    except Exception as e:
        logging.warning(f" Could not remove PID {pid}: {e}")

def cleanup_pid_file():
    """Clean up the PID file"""
    try:
        if os.path.exists(pid_file):
            os.remove(pid_file)
            logging.info(" PID tracking file cleaned up")
    except Exception as e:
        logging.warning(f" Could not clean up PID file: {e}")

# ------------------ Logging ------------------
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, "app.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def handle_exception(exc_type, exc_value, exc_traceback):
    logging.error("[ERROR] Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = handle_exception

def aggressive_cleanup():
    """Ultra-aggressive cleanup that ensures no DDSFocusPro processes remain"""
    logging.info(" Starting aggressive cleanup...")
    
    # Kill all DDSFocusPro processes multiple times
    for round_num in range(7):  # Try 7 rounds of cleanup for PyInstaller
        logging.info(f" Cleanup round {round_num + 1}/7...")
        
        # Method 1: Kill by process name using psutil
        killed_any = False
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'ppid']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower() if proc_info['name'] else ''
                    cmdline_str = ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ''
                    
                    # Check for DDSFocusPro executables or Python processes running our scripts
                    should_kill = False
                    if any(name in proc_name for name in ['connector.exe', 'ddsfocuspro.exe']):
                        should_kill = True
                    elif 'python.exe' in proc_name and any(script in cmdline_str for script in ['app.py', 'desktop.py', 'DDSFocusPro']):
                        should_kill = True
                    elif 'connector' in cmdline_str.lower() or 'ddsfocuspro' in cmdline_str.lower():
                        should_kill = True
                    
                    if should_kill and proc.pid != os.getpid():
                        logging.info(f" Round {round_num + 1}: Killing {proc_name} (PID: {proc_info['pid']})")
                        try:
                            # Kill process tree for PyInstaller
                            try:
                                subprocess.run(['taskkill', '/f', '/t', '/pid', str(proc.pid)], 
                                             capture_output=True, text=True, timeout=3)
                                killed_any = True
                            except:
                                # Fallback to direct process kill
                                proc.terminate()
                                proc.wait(timeout=2)
                                killed_any = True
                        except psutil.TimeoutExpired:
                            try:
                                proc.kill()
                                killed_any = True
                            except:
                                pass
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            logging.warning(f" Error in psutil cleanup round {round_num + 1}: {e}")
        
        # Method 2: Windows taskkill
        try:
            for exe_name in ['connector.exe', 'DDSFocusPro.exe']:
                result = subprocess.run(['taskkill', '/f', '/im', exe_name], 
                                      capture_output=True, text=True, timeout=5)
                if "SUCCESS" in result.stdout:
                    logging.info(f" Round {round_num + 1}: taskkill killed {exe_name}")
                    killed_any = True
        except:
            pass
        
        # Method 3: Kill by port
        try:
            for port in range(5000, 5010):
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, timeout=5)
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) > 4:
                            pid = parts[-1]
                            try:
                                subprocess.run(['taskkill', '/f', '/pid', pid], 
                                             capture_output=True, text=True, timeout=3)
                                logging.info(f" Round {round_num + 1}: Killed process on port {port} (PID: {pid})")
                                killed_any = True
                            except:
                                pass
        except:
            pass
        
        # If no processes were killed in this round, we're done
        if not killed_any:
            logging.info(f" No more processes found after round {round_num + 1}")
            break
        
        # Wait between rounds
        time.sleep(1)
    
    # Final verification
    time.sleep(2)
    remaining_processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            proc_name = proc.info['name'].lower() if proc.info['name'] else ''
            if any(name in proc_name for name in ['connector.exe', 'ddsfocuspro.exe']) and proc.pid != os.getpid():
                remaining_processes.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
    except:
        pass
    
    if remaining_processes:
        logging.warning(f" {len(remaining_processes)} processes still running: {remaining_processes}")
        # As a final measure, force-kill any lingering connector.exe instances
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe']):
                try:
                    name = (proc.info.get('name') or '').lower()
                    cmdline = ' '.join(proc.info.get('cmdline') or [])
                    if 'connector.exe' in name or 'connector' in cmdline.lower():
                        if proc.pid != os.getpid():
                            logging.info(f" Final force kill of lingering process: {proc.info.get('name')} (PID: {proc.pid})")
                            try:
                                subprocess.run(['taskkill', '/f', '/t', '/pid', str(proc.pid)], capture_output=True, text=True, timeout=3)
                            except Exception:
                                try:
                                    proc.kill()
                                except:
                                    pass
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logging.warning(f" Error during final force-kill pass: {e}")
    else:
        logging.info(" Aggressive cleanup completed - no DDSFocusPro processes remaining")

# Global cleanup function that terminates all processes
def cleanup_and_exit():
    """Global cleanup function that terminates all processes"""
    global connector_process, cleanup_in_progress
    
    # Prevent multiple cleanup executions
    if cleanup_in_progress:
        logging.info("[CLEANUP] Cleanup already in progress, skipping...")
        return
    
    cleanup_in_progress = True
    logging.info("[CLEANUP] UI closed by user. Cleaning up ALL connector processes...")
    
    # Step -1: Try to stop active timer gracefully before killing connector
    try:
        import json
        import time
        session_file = "data/current_session.json"
        if os.path.exists(session_file):
            logging.info("[CLEANUP] Active session detected, attempting to stop timer gracefully...")
            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            
            email = session_data.get("email")
            staff_id = session_data.get("staff_id")
            task_id = session_data.get("task_id")
            
            if email and staff_id and task_id:
                end_time = int(time.time())
                payload = {
                    "email": email,
                    "staff_id": staff_id,
                    "task_id": task_id,
                    "end_time": end_time,
                    "note": "Session ended by closing application",
                    "meetings": []
                }
                
                try:
                    response = requests.post(
                        "http://127.0.0.1:5000/end_task_session",
                        json=payload,
                        timeout=2
                    )
                    if response.status_code == 200:
                        logging.info(f"[CLEANUP] Timer stopped successfully for task {task_id}")
                    else:
                        logging.warning(f"[CLEANUP] Timer stop failed: {response.status_code}")
                except Exception as req_error:
                    logging.warning(f"[CLEANUP] Could not reach connector to stop timer: {req_error}")
            
            # Delete session file after attempting to stop
            try:
                os.remove(session_file)
                logging.info("[CLEANUP] Session file cleaned up")
            except:
                pass
    except Exception as session_error:
        logging.warning(f"[CLEANUP] Error handling session cleanup: {session_error}")
    
    # Stop system tray icon
    stop_tray_icon()

    # Step 0: Load any previously tracked PIDs
    load_pids()

    # AGGRESSIVE CLEANUP: Kill ALL connector.exe processes immediately using taskkill
    try:
        logging.info("[CLEANUP] Force killing all connector.exe processes with taskkill...")
        for attempt in range(5):
            result = subprocess.run(
                ['taskkill', '/F', '/IM', 'connector.exe', '/T'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "SUCCESS" in result.stdout or "not found" in result.stderr.lower():
                logging.info(f"[CLEANUP] Taskkill attempt {attempt + 1}: {result.stdout.strip()}")
                break
            time.sleep(0.5)
    except Exception as e:
        logging.warning(f"[CLEANUP] Taskkill error: {e}")

    # Step 1: Kill tracked Flask processes by PID
    try:
        if flask_pids:
            logging.info(f"[CLEANUP] Killing tracked Flask processes: {flask_pids}")
            for pid in flask_pids.copy():
                try:
                    # Use taskkill with /T to kill process tree
                    subprocess.run(['taskkill', '/F', '/PID', str(pid), '/T'], 
                                 capture_output=True, timeout=3)
                    logging.info(f"[CLEANUP] Killed tracked process PID {pid}")
                    remove_pid(pid)
                except Exception as e:
                    logging.warning(f"[CLEANUP] Error killing tracked PID {pid}: {e}")
                    try:
                        # Fallback to psutil
                        process = psutil.Process(pid)
                        process.kill()
                        remove_pid(pid)
                    except:
                        pass
    except Exception as e:
        logging.warning(f"[CLEANUP] Error in tracked PID cleanup: {e}")

    # Step 2: Kill the subprocess if it's still running
    if connector_process and connector_process.poll() is None:
        try:
            logging.info(f"[CLEANUP] Killing subprocess PID {connector_process.pid}...")
            subprocess.run(['taskkill', '/F', '/PID', str(connector_process.pid), '/T'],
                         capture_output=True, timeout=3)
            connector_process.wait(timeout=2)
            logging.info("[CLEANUP] Subprocess killed")
        except Exception as e:
            logging.warning(f"[CLEANUP] Error killing subprocess: {e}")

    # Step 3: Comprehensive background process cleanup using psutil
    try:
        logging.info("[CLEANUP] Killing all remaining connector processes with psutil...")
        killed_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_info = proc.info
                proc_name = proc_info['name'].lower() if proc_info['name'] else ""
                cmdline_str = ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ""
                
                # Check for DDSFocusPro executables and related processes
                should_kill = False
                if any(name in proc_name for name in ['connector.exe', 'ddsfocuspro.exe']):
                    should_kill = True
                elif 'python.exe' in proc_name and any(script in cmdline_str for script in ['app.py', 'connector.py']):
                    should_kill = True
                
                if should_kill and proc.pid != os.getpid():
                    logging.info(f"[CLEANUP] Killing {proc_name} (PID: {proc_info['pid']})")
                    try:
                        # Use taskkill for Windows
                        subprocess.run(['taskkill', '/F', '/PID', str(proc.pid), '/T'],
                                     capture_output=True, timeout=2)
                        killed_count += 1
                    except:
                        # Fallback to psutil
                        proc.kill()
                        killed_count += 1
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        logging.info(f"[CLEANUP] Killed {killed_count} connector processes")
                    
    except Exception as e:
        logging.warning(f"[CLEANUP] Error during process cleanup: {e}")

    # Step 4: Final aggressive cleanup
    logging.info("[CLEANUP] Running final aggressive cleanup...")
    aggressive_cleanup()
    
    # Step 5: Clean up PID tracking file
    cleanup_pid_file()
    
    logging.info("[CLEANUP] All cleanup completed. Exiting application...")
    
    # Final exit
    try:
        sys.exit(0)
    except:
        os._exit(0)
    aggressive_cleanup()
    
    # Final step: Clean up PID tracking file
    cleanup_pid_file()
    
    # Final exit
    try:
        sys.exit(0)
    except:
        try:
            os._exit(0)
        except:
            # Last resort - Windows specific
            try:
                subprocess.run(['taskkill', '/f', '/pid', str(os.getpid())], 
                             capture_output=True, text=True, timeout=2)
            except:
                pass

def monitor_main_process():
    """Monitor if the main GUI process is still alive and cleanup if not"""
    current_pid = os.getpid()
    
    while True:
        try:
            time.sleep(3)  # Check every 3 seconds (more frequent)
            
            # Check if our own process is still running normally
            if not psutil.pid_exists(current_pid):
                logging.info("[MONITOR] Main process no longer exists, triggering cleanup")
                cleanup_background_processes()
                break
                
            # Check if we should exit (this can be set by other parts of the code)
            if cleanup_in_progress:
                break
                
            # Proactive cleanup: Check for orphaned DDSFocusPro processes
            orphaned_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ""
                    if 'connector.exe' in proc_name and proc.pid != current_pid:
                        orphaned_count += 1
                except:
                    continue
            
            # If we find too many orphaned processes, clean them up
            if orphaned_count > 2:  # More than 2 background processes is suspicious
                logging.info(f"[MONITOR] Found {orphaned_count} orphaned DDSFocusPro processes, cleaning up...")
                cleanup_background_processes()
                
        except Exception as e:
            logging.warning(f"[MONITOR] Error in process monitoring: {e}")
            continue

def cleanup_background_processes():
    """Cleanup only background processes without exiting the main process"""
    try:
        logging.info(" Emergency cleanup of background processes...")
        
        # Method 1: Kill connector processes using multiple approaches
        for attempt in range(3):
            try:
                result = subprocess.run(['taskkill', '/f', '/im', 'connector.exe'], 
                                      capture_output=True, text=True, timeout=5)
                if "SUCCESS" in result.stdout:
                    logging.info(f" Emergency taskkill successful (attempt {attempt + 1})")
                    break
            except:
                continue
        
        # Method 2: Kill by process name using psutil - More aggressive
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_info = proc.info
                proc_name = proc_info['name'].lower() if proc_info['name'] else ""
                
                if ('connector.exe' in proc_name or 'ddsfocuspro' in proc_name) and proc.pid != os.getpid():
                    proc.kill()
                    killed_count += 1
                    logging.info(f" Emergency killed: {proc_name} (PID: {proc_info['pid']})")
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        logging.info(f" Emergency cleanup completed. Killed {killed_count} background processes.")
                    
    except Exception as e:
        logging.warning(f" Error during emergency cleanup: {e}")

# Signal handlers for proper cleanup
def signal_handler(signum, frame):
    logging.info(f"[SIGNAL] Received signal {signum}, cleaning up...")
    cleanup_and_exit()

# Register signal handlers (Windows compatible)
try:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    logging.info("[OK] Signal handlers registered")
except Exception as e:
    logging.warning(f"[WARN] Could not register signal handlers: {e}")

# Register atexit handler for additional safety
try:
    atexit.register(cleanup_and_exit)
    logging.info("[OK] Exit handler registered")
except Exception as e:
    logging.warning(f"[WARN] Could not register exit handler: {e}")

def start_flask():
    global connector_process
    
    # Method 0: Simple file lock to prevent race conditions
    lock_file = "connector_starting.lock"
    try:
        if os.path.exists(lock_file):
            # Check if lock is stale (older than 30 seconds)
            lock_age = time.time() - os.path.getmtime(lock_file)
            if lock_age > 30:
                os.remove(lock_file)
                logging.info(" Removed stale connector lock file")
            else:
                logging.info(" Connector startup already in progress (lock file exists)")
                return
        
        # Create lock file
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        logging.info(" Created connector startup lock")
        
    except Exception as e:
        logging.warning(f" Could not create startup lock: {e}")
    
    try:
        # Check if connector is already running - SIMPLIFIED detection
        connector_already_running = False
        flask_working_port = None
    
        # Only check Flask endpoint to see if connector is actually serving
        try:
            import requests
            test_ports = [5000, 5001, 5002, 5003, 5004, 5005]
            for port in test_ports:
                try:
                    response = requests.get(f"http://127.0.0.1:{port}", timeout=2)
                    if response.status_code == 200:
                        connector_already_running = True
                        flask_working_port = port
                        logging.info(f" Connector confirmed running on port {port}")
                        break
                except requests.exceptions.RequestException:
                    continue
        except Exception as e:
            logging.warning(f"Error checking for Flask endpoint: {e}")
        
        if connector_already_running:
            logging.info(f" Using existing connector instance on port {flask_working_port}")
            return
        
        # Force start connector - no process detection to avoid false positives
        logging.info(" No active connector found - starting new connector instance")
        
        logging.info(f"[FLASK] Starting Flask server...")
        
        # Define paths for finding connector.exe
        base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
        current_dir = os.getcwd()
        logging.info(f"[DEBUG] Base path: {base_path}")
        logging.info(f"[DEBUG] Current working directory: {current_dir}")
        
        # Look for connector.exe executable
        possible_executables = [
            os.path.join(current_dir, "connector.exe"),  # Current working directory
            os.path.join(base_path, "connector.exe"),    # Executable directory
            os.path.join(os.path.dirname(base_path), "connector.exe"),  # Parent directory
            os.path.join(current_dir, "dist", "connector.exe"),  # Dist folder
            os.path.join(base_path, "dist", "connector.exe"),    # Dist folder from base
        ]
        
        app_executable = None
        for exe_path in possible_executables:
            logging.info(f"[DEBUG] Checking for connector.exe at: {exe_path}")
            if os.path.exists(exe_path):
                app_executable = exe_path
                logging.info(f"[FOUND] connector.exe found at: {app_executable}")
                break
        
        if app_executable:
            logging.info(f"[FLASK] Starting Flask executable: {app_executable}")
            
            # Hide the connector console window for silent operation
            import subprocess
            
            connector_process = subprocess.Popen(
                [app_executable],
                cwd=os.path.dirname(app_executable),
                creationflags=subprocess.CREATE_NO_WINDOW  # Hide console window
            )
            logging.info(f"[OK] Flask executable started with PID: {connector_process.pid} (HIDDEN)")
            save_pid(connector_process.pid)  # Track this PID (parent)

            # PyInstaller onefile creates a parent and a child process. Wait briefly
            # and detect any additional connector.exe child processes so we can
            # track and clean them up later.
            try:
                time.sleep(1)
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe']):
                    try:
                        name = (proc.info.get('name') or '').lower()
                        cmdline = ' '.join(proc.info.get('cmdline') or [])
                        exe_path = proc.info.get('exe') or ''

                        matches_executable = False
                        # Match by executable path
                        if exe_path and os.path.abspath(exe_path) == os.path.abspath(app_executable):
                            matches_executable = True
                        # Match by process name or cmdline containing connector
                        if 'connector.exe' in name or 'connector.exe' in cmdline.lower() or 'connector' in cmdline.lower():
                            matches_executable = True

                        if matches_executable and proc.pid != os.getpid():
                            if proc.pid not in flask_pids:
                                save_pid(proc.pid)
                                logging.info(f"[OK] Detected and tracked connector PID: {proc.pid}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception as e:
                logging.warning(f" Error detecting connector child processes: {e}")
        else:
            # Fallback: Try to run app.py directly if executable not found
            logging.warning("[WARN] connector.exe not found, trying app.py...")
            
            possible_app_paths = [
                os.path.join(current_dir, "app.py"),
                os.path.join(base_path, "app.py"),
            ]
            
            app_path = None
            for path in possible_app_paths:
                if os.path.exists(path):
                    app_path = path
                    break
            
            if app_path:
                logging.info(f"[FLASK] Starting Flask from app.py: {app_path}")
                
                # Hide the connector console window for silent operation
                import subprocess
                
                connector_process = subprocess.Popen(
                    [sys.executable, app_path],
                    cwd=os.path.dirname(app_path),
                    creationflags=subprocess.CREATE_NO_WINDOW  # Hide console window
                )
                logging.info(f"[OK] Flask app.py started with PID: {connector_process.pid} (HIDDEN)")
                save_pid(connector_process.pid)  # Track this PID
            else:
                logging.error("[ERROR] No Flask app found (neither executable nor app.py)!")
                return
                
    except Exception as e:
        logging.error(f"[ERROR] Failed to start Flask: {e}")
    finally:
        # Clean up lock file
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
                logging.info(" Removed connector startup lock")
        except Exception as e:
            logging.warning(f" Could not remove startup lock: {e}")

# ------------------ Background Flask Monitor ------------------
def wait_until_flask_ready(max_wait=float("inf")):
    global flask_ready
    start_time = time.time()
    
    # Check multiple ports since app now finds free ports
    ports_to_check = [5000, 5001, 5002, 5003, 5004, 5005]
    
    while time.time() - start_time < max_wait:
        for port in ports_to_check:
            try:
                r = requests.get(f"http://127.0.0.1:{port}", timeout=2)
                if r.status_code == 200:
                    flask_ready = True
                    logging.info(f"[OK] Flask ready on port {port}")
                    return f"http://127.0.0.1:{port}"
            except:
                pass  # no log here
        time.sleep(1)
        
        # Show progress every 5 seconds
        elapsed = time.time() - start_time
        if int(elapsed) % 5 == 0:
            logging.info(f"[WAIT] Still waiting for Flask... ({int(elapsed)}s)")
    
    logging.warning("[TIMEOUT] Timeout: Flask not ready in time")
    return None


def background_launcher():
    global flask_ready
    start_flask()
    flask_url = wait_until_flask_ready(60)  # Wait max 60 seconds

    
    if flask_ready and flask_url:
        logging.info(f"🌐 Opening main app window at {flask_url}")
        webview.windows[0].load_url(flask_url)
    else:
        logging.warning("[ERROR] Flask did not respond in time. Keeping loader visible.")




# ------------------ Main Launcher ------------------
if __name__ == '__main__':
    # Step 1: Open exec terminal first
    logging.info(" Starting DDS Focus Pro with exec terminal...")
    open_exec_terminal()
    
    # Step 2: Clean up any orphaned processes from previous runs (but not active connectors)
    load_pids()
    if flask_pids:
        logging.info(f" Cleaning up {len(flask_pids)} orphaned processes from previous runs")
        # Only cleanup truly orphaned processes, not active ones
        active_pids = []
        for pid in flask_pids.copy():
            try:
                proc = psutil.Process(pid)
                if proc.is_running():
                    active_pids.append(pid)
                else:
                    flask_pids.discard(pid)  # Remove dead PIDs
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                flask_pids.discard(pid)  # Remove invalid PIDs
        
        if active_pids:
            logging.info(f" Found {len(active_pids)} active connector processes - preserving them")
        flask_pids.clear()  # Reset for new session
        cleanup_in_progress = False  # Reset flag
    
    # Step 3: Start connector immediately (synchronous) so user doesn't need to open it manually,
    # then start a background thread to wait until Flask is ready and load the UI.
    try:
        start_flask()
    except Exception as e:
        logging.warning(f" start_flask() raised an exception: {e}")

    def _wait_and_open():
        flask_url = wait_until_flask_ready(60)
        if flask_url:
            try:
                logging.info(f"🌐 Opening main app window at {flask_url}")
                webview.windows[0].load_url(flask_url)
            except Exception as e:
                logging.warning(f" Could not load URL into webview: {e}")
        else:
            logging.warning("[ERROR] Flask did not respond in time. Keeping loader visible.")

    threading.Thread(target=_wait_and_open, daemon=True).start()
    
    # Step 4: Start process monitoring for cleanup
    threading.Thread(target=monitor_main_process, daemon=True).start()
    logging.info(" Process monitoring started")
    
    # Step 5: Start system tray icon BEFORE window creation
    if TRAY_AVAILABLE:
        tray_thread = threading.Thread(target=run_tray_icon, daemon=True)
        tray_thread.start()
        logging.info("[TRAY] System tray thread started")
        # Give tray icon a moment to initialize
        time.sleep(0.5)
    else:
        logging.info("[TRAY] System tray not available - skipping")

    # Step 6: Show UI immediately (no wait)
    try:
        # Try multiple locations for loader.html
        current_dir = os.getcwd()
        possible_loader_paths = [
            os.path.join(current_dir, "templates", "loader.html"),
            os.path.join(os.path.dirname(__file__), "templates", "loader.html"),
            os.path.join(os.path.dirname(sys.executable), "templates", "loader.html") if getattr(sys, 'frozen', False) else None,
        ]
        
        loader_path = None
        for path in possible_loader_paths:
            if path and os.path.exists(path):
                loader_path = path
                break
        
        if not loader_path:
            logging.error(f"[ERROR] loader.html NOT FOUND in any of these locations:")
            for path in possible_loader_paths:
                if path:
                    logging.error(f"  - {path}")
            raise FileNotFoundError("loader.html missing.")

        logging.info(f"[OK] loader.html found at {loader_path}")

        with open(loader_path, "r", encoding="utf-8") as f:
            loader_html = f.read()

        webview.create_window(
            title="DDS FocusPro",
            html=loader_html,
            width=1024,
            height=750,
            on_top=False,
            resizable=True
        )

        # [OK] Attach cleanup after window opens
        def after_window_created():
            try:
                if webview.windows:
                    # Set up proper window close event handler
                    def on_window_close():
                        logging.info("[OK] Window close event triggered by user - shutting down all processes")
                        # Always cleanup and exit when window is closed
                        cleanup_and_exit()
                        # Force exit to ensure everything stops
                        try:
                            os._exit(0)
                        except:
                            sys.exit(0)
                    
                    webview.windows[0].events.closed += on_window_close
                    logging.info("[OK] Window close event handler attached - will terminate all processes on close")
                else:
                    logging.warning("[WARN] No webview windows found for event attachment")
            except Exception as e:
                logging.error(f"[ERROR] Failed to attach window close handler: {e}")

        webview.start(gui='edgechromium', debug=False, func=after_window_created)
        
        # If webview.start() returns normally (window was closed), cleanup
        logging.info("[INFO] WebView window closed normally")
        cleanup_and_exit()

    except Exception as e:
        logging.error(f"[ERROR] WebView failed: {e}")
        # Ensure cleanup happens even if webview fails
        cleanup_and_exit()
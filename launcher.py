import subprocess
import time
import webbrowser
import sys
import os
import socket

def wait_for_server(host="127.0.0.1", port=7860, timeout=15):
    """Wait for the server to actually be ready"""
    print(f"⏳ Waiting for server at {host}:{port}...")
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                print("✅ Server is ready!")
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.5)
            print("   .", end="", flush=True)
    
    print(f"\n⚠️ Server didn't respond within {timeout} seconds, trying browser anyway...")
    return False

def open_browser_robust(url):
    """Use the same methods that work in debug.exe"""
    print(f"🌐 Opening browser to {url}")
    
    # Method 1: Standard webbrowser
    try:
        webbrowser.open(url)
        print("✅ Browser opened with webbrowser.open()")
        return True
    except Exception as e:
        print(f"⚠️ webbrowser.open() failed: {e}")
    
    # Method 2: System command (this works in debug.exe)
    try:
        if sys.platform == "win32":
            os.startfile(url)
            print("✅ Browser opened with os.startfile()")
            return True
        elif sys.platform == "darwin":
            subprocess.call(["open", url])
            print("✅ Browser opened with 'open' command")
            return True
        else:
            subprocess.call(["xdg-open", url])
            print("✅ Browser opened with 'xdg-open'")
            return True
    except Exception as e:
        print(f"⚠️ System command failed: {e}")
    
    # Method 3: Direct subprocess (backup)
    try:
        if sys.platform == "win32":
            subprocess.Popen(['cmd', '/c', 'start', url], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            print("✅ Browser opened with cmd start")
            return True
        else:
            subprocess.Popen(['python', '-m', 'webbrowser', url])
            print("✅ Browser opened with python -m webbrowser")
            return True
    except Exception as e:
        print(f"⚠️ Direct subprocess failed: {e}")
    
    return False

def main():
    print("=" * 60)
    print("🎨 Asemic Artist Pro Launcher")
    print("=" * 60)
    
    is_frozen = getattr(sys, 'frozen', False)
    
    # Start the main app
    if is_frozen:
        # Running as launcher.exe - find and start app.exe
        exe_dir = os.path.dirname(sys.executable)
        possible_paths = [
            os.path.join(exe_dir, 'app.exe'),
            os.path.join(exe_dir, '..', 'app.exe'),
            os.path.join(os.getcwd(), 'app.exe'),
            'app.exe'
        ]
        
        app_path = None
        for path in possible_paths:
            if os.path.exists(path):
                app_path = path
                break
        
        if not app_path:
            print("❌ Could not find app.exe!")
            print("   Searched in:")
            for path in possible_paths:
                print(f"   - {path}")
            input("Press Enter to exit...")
            return
        
        print(f"🚀 Starting {app_path}")
        try:
            # Start app.exe with DISABLE_BROWSER environment variable
            env = os.environ.copy()
            env['DISABLE_BROWSER'] = '1'  # Tell app.exe not to open browser
            
            if sys.platform == "win32":
                subprocess.Popen([app_path], env=env,
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([app_path], env=env)
            print("✅ App started")
        except Exception as e:
            print(f"❌ Failed to start app: {e}")
            input("Press Enter to exit...")
            return
    else:
        # Running as python launcher.py - start app.py with disabled browser
        print("🐍 Starting app.py with browser disabled...")
        env = os.environ.copy()
        env['DISABLE_BROWSER'] = '1'  # Tell app.py not to open browser
        subprocess.Popen([sys.executable, 'app.py'], env=env)
        print("✅ App started")
    
    # Wait for server to be ready
    server_ready = wait_for_server()
    
    # Now open browser using robust method
    url = "http://127.0.0.1:7860"
    browser_opened = open_browser_robust(url)
    
    print("=" * 60)
    if browser_opened:
        print("🎉 Asemic Artist Pro is now running!")
        print(f"🌐 Web interface: {url}")
        print("📱 You can close this launcher window")
        print("🛑 To stop the app, close the app console window")
    else:
        print("⚠️ Could not automatically open browser")
        print(f"👆 Please manually open: {url}")
        print("📱 The app should still be running")
    
    print("=" * 60)
    input("Press Enter to exit launcher...")

if __name__ == "__main__":
    main()



# import subprocess
# import time
# import webbrowser
# import sys
# import os

# def main():
#     print("Starting Asemic Artist...")
    
#     # Start the main app in background
#     if getattr(sys, 'frozen', False):
#         # Running as exe - start the main app
#         app_path = os.path.join(os.path.dirname(sys.executable), 'app.exe')
#         if not os.path.exists(app_path):
#             app_path = 'app.exe'  # Try current directory
        
#         print(f"Launching {app_path}")
#         subprocess.Popen([app_path], creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
#     else:
#         # Running as script
#         subprocess.Popen([sys.executable, 'app.py'])
    
#     # Wait a bit then open browser
#     print("Waiting for server to start...")
#     time.sleep(5)
    
#     print("Opening browser...")
#     try:
#         webbrowser.open("http://127.0.0.1:7860")
#         print("✓ Browser opened")
#     except Exception as e:
#         print(f"Browser opening failed: {e}")
#         if sys.platform == "win32":
#             os.system("start http://127.0.0.1:7860")
    
#     print("Done! The application should now be running.")
#     input("Press Enter to exit launcher...")

# if __name__ == "__main__":
#     main()
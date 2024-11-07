import threading
import webview
from ui.dashboard import run_dash

# Start Dash server in a separate thread
dash_thread = threading.Thread(target=run_dash)
dash_thread.daemon = True
dash_thread.start()

# Create a fullscreen PyWebView window with the custom icon
webview.create_window("Bank Transaction Dashboard", "http://127.0.0.1:8051", width=1920, height=1080, resizable=True,
                      frameless=False)

webview.start()
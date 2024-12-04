import tkinter as tk
from tkinter import ttk
import time
from threading import Thread
from collections import defaultdict
import csv
import logging
import Quartz

# Setting up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class AppTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("App Usage Tracker")
        self.root.geometry("500x400")

        self.usage_data = defaultdict(int)
        self.current_app = None
        self.start_time = time.time()
        self.is_tracking = True

        self.label = tk.Label(root, text="Active Applications", font=("Arial", 14))
        self.label.pack(pady=10)

        self.tree = ttk.Treeview(root, columns=("App", "Time"), show="headings", height=10)
        self.tree.heading("App", text="Application")
        self.tree.heading("Time", text="Time")
        self.tree.pack(fill="both", expand=True)

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        self.pause_button = tk.Button(self.button_frame, text="Pause", command=self.toggle_tracking)
        self.pause_button.pack(side="left", padx=5)

        self.save_button = tk.Button(self.button_frame, text="Save Data", command=self.save_data)
        self.save_button.pack(side="left", padx=5)

        self.tracking_thread = Thread(target=self.track_usage)
        self.tracking_thread.daemon = True
        self.tracking_thread.start()

        self.update_ui()

    def track_usage(self):
        while True:
            if not self.is_tracking:
                time.sleep(1)
                continue

            try:
                app_name = self.get_active_window_title()
                if app_name != self.current_app:
                    if self.current_app:
                        self.usage_data[self.current_app] += time.time() - self.start_time
                    self.current_app = app_name
                    self.start_time = time.time()
            except Exception as e:
                logging.error(f"Error: {e}")

            time.sleep(1)

    def get_active_window_title(self):
        """Получает заголовок активного окна на macOS с помощью Quartz."""
        window_info = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID
        )
        for window in window_info:
            if window.get('kCGWindowOwnerName') and window.get('kCGWindowLayer') == 0:
                return window.get('kCGWindowOwnerName', 'Unknown')
        return 'Unknown'

    def format_time(self, seconds):
        if seconds < 60:
            return f"{int(seconds)} sec"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{int(minutes)} min"
        else:
            hours = seconds // 3600
            return f"{int(hours)} hour"

    def update_ui(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for app, duration in self.usage_data.items():
            formatted_time = self.format_time(duration)
            self.tree.insert("", "end", values=(app, formatted_time))

        self.root.after(2000, self.update_ui)

    def toggle_tracking(self):
        self.is_tracking = not self.is_tracking
        self.pause_button.config(text="Resume" if not self.is_tracking else "Pause")

    def save_data(self):
        with open("app_usage_data.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Application", "Time Spent"])
            for app, duration in self.usage_data.items():
                writer.writerow([app, self.format_time(duration)])
        logging.info("Data saved to app_usage_data.csv")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppTracker(root)
    root.mainloop()
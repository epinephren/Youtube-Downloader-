import os
import re
import sys
import subprocess
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk


class YtDlpGui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Simple yt-dlp GUI")
        self.geometry("860x660")

        self.process = None
        self.log_queue = queue.Queue()
        self.status_queue = queue.Queue()

        self.url_var = tk.StringVar()
        self.output_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.quality_var = tk.StringVar(value="best")
        self.audio_only_var = tk.BooleanVar(value=False)
        self.auto_update_var = tk.BooleanVar(value=True)
        self.use_ejs_var = tk.BooleanVar(value=True)
        self.use_cookies_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0)

        self.build_ui()
        self.after(100, self.process_queues)

        if self.auto_update_var.get():
            self.update_ytdlp_async()

    def build_ui(self):
        pad = {"padx": 10, "pady": 6}

        tk.Label(self, text="YouTube URL / Playlist URL").pack(anchor="w", **pad)
        tk.Entry(self, textvariable=self.url_var).pack(fill="x", padx=10)

        folder_frame = tk.Frame(self)
        folder_frame.pack(fill="x", **pad)

        tk.Label(folder_frame, text="Output:").pack(side="left")
        tk.Entry(folder_frame, textvariable=self.output_var).pack(side="left", fill="x", expand=True, padx=8)
        tk.Button(folder_frame, text="Browse", command=self.choose_folder).pack(side="right")

        options_frame = tk.Frame(self)
        options_frame.pack(fill="x", **pad)

        tk.Label(options_frame, text="Quality:").pack(side="left")
        tk.OptionMenu(options_frame, self.quality_var, "best", "1080p", "720p", "audio").pack(side="left", padx=8)

        tk.Checkbutton(
            options_frame,
            text="Audio only (MP3)",
            variable=self.audio_only_var,
        ).pack(side="left", padx=12)

        tk.Checkbutton(
            options_frame,
            text="Use YouTube EJS solver",
            variable=self.use_ejs_var,
        ).pack(side="left", padx=12)

        second_options_frame = tk.Frame(self)
        second_options_frame.pack(fill="x", padx=10, pady=2)

        tk.Checkbutton(
            second_options_frame,
            text="Use Firefox cookies",
            variable=self.use_cookies_var,
        ).pack(side="left")

        tk.Checkbutton(
            second_options_frame,
            text="Auto-update yt-dlp on start",
            variable=self.auto_update_var,
        ).pack(side="left", padx=12)

        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", **pad)

        tk.Button(button_frame, text="Download", command=self.start_download, width=16).pack(side="left")
        tk.Button(button_frame, text="Update yt-dlp", command=self.update_ytdlp_async, width=16).pack(side="left", padx=8)
        tk.Button(button_frame, text="Stop", command=self.stop_download, width=16).pack(side="left")
        tk.Button(button_frame, text="Clear Log", command=self.clear_log, width=16).pack(side="left", padx=8)

        progress_frame = tk.Frame(self)
        progress_frame.pack(fill="x", padx=10, pady=4)

        self.progress = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(side="left", fill="x", expand=True)

        tk.Label(progress_frame, textvariable=self.status_var, width=28, anchor="e").pack(side="right", padx=8)

        self.log = ScrolledText(self, height=27)
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_var.get())
        if folder:
            self.output_var.set(folder)

    def clear_log(self):
        self.log.delete("1.0", tk.END)

    def python_module_cmd(self):
        # Use the exact Python interpreter running this GUI.
        # This avoids PATH confusion between "python", "py", Microsoft Store Python, and venvs.
        return [sys.executable, "-m", "yt_dlp"]

    def pip_cmd(self):
        return [sys.executable, "-m", "pip"]

    def build_command(self):
        url = self.url_var.get().strip()
        output = self.output_var.get().strip()

        if not url:
            raise ValueError("Please enter a URL.")
        if not output:
            raise ValueError("Please choose an output folder.")

        os.makedirs(output, exist_ok=True)

        cmd = self.python_module_cmd() + [
            "--newline",
            "--no-color",
            "-o",
            os.path.join(output, "%(title)s.%(ext)s"),
        ]

        if self.use_ejs_var.get():
            cmd += [
                "--js-runtimes", "node",
                "--remote-components", "ejs:github",
            ]

        if self.use_cookies_var.get():
            cmd += ["--cookies-from-browser", "firefox"]

        if self.audio_only_var.get() or self.quality_var.get() == "audio":
            cmd += [
                "-x",
                "--audio-format", "mp3",
                "--audio-quality", "0",
            ]
        else:
            quality = self.quality_var.get()

            if quality == "1080p":
                cmd += ["-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"]
            elif quality == "720p":
                cmd += ["-f", "bestvideo[height<=720]+bestaudio/best[height<=720]/best"]
            else:
                cmd += ["-f", "bestvideo+bestaudio/best"]

            cmd += ["--merge-output-format", "mp4"]

        cmd.append(url)
        return cmd

    def update_ytdlp_async(self):
        if self.is_process_running():
            messagebox.showwarning("Busy", "A download/update is already running.")
            return

        thread = threading.Thread(target=self.update_ytdlp, daemon=True)
        thread.start()

    def update_ytdlp(self):
        self.status("Updating yt-dlp...")
        self.write_log("Updating yt-dlp and EJS solver...\n")

        cmd = self.pip_cmd() + [
            "install",
            "-U",
            "yt-dlp",
            "yt-dlp-ejs",
        ]

        self.run_command(cmd, is_download=False)
        self.status("Ready")

    def start_download(self):
        if self.is_process_running():
            messagebox.showwarning("Download running", "A download/update is already running.")
            return

        try:
            cmd = self.build_command()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        self.progress_var.set(0)
        self.status("Starting...")

        self.write_log("Starting:\n")
        self.write_log(self.format_command_for_log(cmd) + "\n\n")

        thread = threading.Thread(target=self.run_command, args=(cmd, True), daemon=True)
        thread.start()

    def run_command(self, cmd, is_download=True):
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=self.get_creation_flags(),
            )

            assert self.process.stdout is not None

            for line in self.process.stdout:
                self.write_log(line)
                if is_download:
                    self.parse_progress(line)

            code = self.process.wait()

            if is_download:
                self.status("Done" if code == 0 else f"Error {code}")

            self.write_log(f"\nFinished with exit code {code}\n")

            if code != 0 and is_download:
                self.write_log(
                    "\nHint: If YouTube says the video is unavailable, try enabling "
                    "'Use Firefox cookies' after logging into YouTube in Firefox.\n"
                )

        except FileNotFoundError:
            self.write_log(
                "\nERROR: Python or yt-dlp was not found.\n"
                "Try pressing 'Update yt-dlp' or run:\n"
                f'"{sys.executable}" -m pip install -U yt-dlp yt-dlp-ejs\n'
            )
            self.status("Error")
        except Exception as exc:
            self.write_log(f"\nERROR: {exc}\n")
            self.status("Error")
        finally:
            self.process = None

    def parse_progress(self, line):
        # Example:
        # [download]  42.1% of 123.45MiB at 5.67MiB/s ETA 00:12
        match = re.search(r"\[download\]\s+(\d+(?:\.\d+)?)%", line)
        if match:
            percent = float(match.group(1))
            self.progress_var.set(percent)
            self.status(f"{percent:.1f}%")
            return

        if "[download] 100%" in line or "has already been downloaded" in line:
            self.progress_var.set(100)
            self.status("100%")
        elif "Downloading playlist" in line:
            self.status("Playlist")
        elif "Extracting URL" in line:
            self.status("Extracting")
        elif "Downloading webpage" in line:
            self.status("Webpage")
        elif "Downloading player" in line:
            self.status("Player")
        elif "Merging formats" in line:
            self.status("Merging")
        elif "Deleting original file" in line:
            self.status("Cleanup")
        elif "ERROR:" in line:
            self.status("Error")
        elif "WARNING:" in line and "challenge" in line.lower():
            self.status("Challenge warning")

    def stop_download(self):
        if self.is_process_running():
            self.write_log("\nStopping...\n")
            self.status("Stopping")

            try:
                self.process.terminate()
            except Exception as exc:
                self.write_log(f"\nERROR while stopping: {exc}\n")
                self.status("Error")

    def is_process_running(self):
        return self.process is not None and self.process.poll() is None

    def write_log(self, text):
        self.log_queue.put(text)

    def status(self, text):
        self.status_queue.put(text)

    def process_queues(self):
        try:
            while True:
                text = self.log_queue.get_nowait()
                self.log.insert(tk.END, text)
                self.log.see(tk.END)
        except queue.Empty:
            pass

        try:
            while True:
                text = self.status_queue.get_nowait()
                self.status_var.set(text)
        except queue.Empty:
            pass

        self.after(100, self.process_queues)

    @staticmethod
    def format_command_for_log(cmd):
        return " ".join(f'"{part}"' if " " in part else part for part in cmd)

    @staticmethod
    def get_creation_flags():
        if os.name == "nt":
            return subprocess.CREATE_NO_WINDOW
        return 0


if __name__ == "__main__":
    app = YtDlpGui()
    app.mainloop()

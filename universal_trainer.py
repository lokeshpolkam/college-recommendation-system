#!/usr/bin/env python3
"""
Universal Trainer + UI
- Cross-platform (Windows / macOS / Linux)
- Auto-detects a folder named 'dataset' in the same directory (or any subdirectory)
- Saves training output directly into that 'dataset' folder (no "where to save" prompts)
- Pretty Tkinter UI with embedded artwork (no external image files required, but Pillow used if available)
- Non-blocking training loop (uses threading) with a fake training routine you can replace with your real code

How to use:
1. Put this file next to your 'dataset' folder (or anywhere). If 'dataset' exists somewhere under the chosen path it will be used.
2. Run: python universal_trainer_ui.py
3. If the script cannot find a 'dataset' folder automatically, it will show a button to let you choose one.

Dependencies (optional):
- Pillow (pip install pillow) used to render embedded PNG nicely; if not installed, the UI still works.

Drop-in: replace `fake_train()` with your real training function. The training function will be given two arguments: `dataset_dir` (pathlib.Path) and `progress_callback(percent, message)` to update the UI.

"""

import sys
import threading
import time
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import base64
import io

# Try to import PIL for nicer image handling, but keep optional
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# ----------------------------- Embedded artwork (small) -----------------------------
# A tiny base64-encoded PNG (a simple abstract logo). You can replace or extend this.
EMBEDDED_PNG = (
    b'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAABKUlEQVR4nO3XQQrCQBRE0fSg'
    b'F4g2qW3uS0b2QXg6QdJgkQXNw1Uuv1vN6+f2w8s7s7k3N2dmZkYGBgYGBgYGBgYGBgYGBgYG'
    b'BgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgaGg/qw3oG0xgkfQjHkI65D8QjHkI65D'
    b'8QjHkI65D8QjHkI65D8QjHkI65D8QjHkI65D8QjHkI65D8QjHkI65D8QjHkI65D8QjHkI65D8'
    b'QjHkI65D8QjHkI65D8QjHkI65D8QjHkI65D8QjHkI65D8QjHkI65D8QjHkI65D8QjHn8fWn'
    b'0BTrwJjF4gNnTAAAAAElFTkSuQmCC'
)

# ----------------------------- Utility functions -----------------------------

def find_dataset_dir(start_path: Path) -> Path | None:
    """Search recursively from start_path for a directory named exactly 'dataset'.
    Return the first match as Path, or None if not found.
    """
    start_path = start_path.resolve()
    # check current folder first
    candidate = start_path / 'dataset'
    if candidate.is_dir():
        return candidate
    # walk depth-first but avoid very deep system dirs
    for p in start_path.rglob('dataset'):
        if p.is_dir():
            return p
    return None


def safe_write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    with tmp.open('w', encoding='utf8') as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)


# ----------------------------- Fake training function (to replace) -----------------------------

def fake_train(dataset_dir: Path, progress_callback):
    """A placeholder training routine. Replace with your real training loop.
    Use `progress_callback(percent, message)` to update UI.
    The function will save a dummy 'model.bin' and 'training_info.json' to dataset_dir/trained/
    """
    trained_dir = dataset_dir / 'trained'
    trained_dir.mkdir(parents=True, exist_ok=True)

    total_steps = 20
    for step in range(1, total_steps + 1):
        # simulate work
        time.sleep(0.15)
        pct = int(step / total_steps * 100)
        progress_callback(pct, f"Step {step}/{total_steps}")

    # write dummy model file
    model_path = trained_dir / 'model.bin'
    with model_path.open('wb') as f:
        f.write(b"THIS_IS_A_DUMMY_MODEL\n")

    # write metadata
    info = {
        'model_file': str(model_path.name),
        'trained_at': time.asctime(),
        'notes': 'This is a dummy training output. Replace fake_train with real trainer.'
    }
    safe_write_json(trained_dir / 'training_info.json', info)

    progress_callback(100, 'Finished')
    return trained_dir


# ----------------------------- GUI -----------------------------

class TrainerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Universal Trainer — cross-platform')
        self.geometry('720x420')
        self.minsize(640, 360)

        # style
        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam')
        except Exception:
            pass

        # top frame with artwork and title
        top = ttk.Frame(self, padding=12)
        top.pack(fill='x')

        # artwork
        art_img = self._load_embedded_image(96)
        if art_img:
            lbl_art = ttk.Label(top, image=art_img)
            lbl_art.image = art_img
            lbl_art.pack(side='left', padx=(0, 12))

        title_frame = ttk.Frame(top)
        title_frame.pack(side='left', fill='x', expand=True)
        ttk.Label(title_frame, text='Universal Trainer', font=('Helvetica', 20, 'bold')).pack(anchor='w')
        ttk.Label(title_frame, text='Auto-detect dataset folder and save training there — cross-platform', wraplength=520).pack(anchor='w', pady=(6,0))

        # main content
        main = ttk.Frame(self, padding=(12,6))
        main.pack(fill='both', expand=True)

        # dataset path display
        self.dataset_var = tk.StringVar(value='(searching for dataset...)')
        ds_frame = ttk.Frame(main)
        ds_frame.pack(fill='x', pady=(4,8))
        ttk.Label(ds_frame, text='Dataset folder:').pack(side='left')
        ttk.Label(ds_frame, textvariable=self.dataset_var, foreground='#055', wraplength=480).pack(side='left', padx=(8,4))
        ttk.Button(ds_frame, text='Choose another', command=self.choose_dataset).pack(side='right')

        # controls
        ctrl_frame = ttk.LabelFrame(main, text='Training controls', padding=10)
        ctrl_frame.pack(fill='x', pady=(6,12))

        ttk.Label(ctrl_frame, text='Model name:').grid(row=0, column=0, sticky='w')
        self.model_name = tk.StringVar(value='my_model')
        ttk.Entry(ctrl_frame, textvariable=self.model_name, width=28).grid(row=0, column=1, sticky='w', padx=(8,12))

        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ctrl_frame, text='Auto-save outputs into dataset/trained/', variable=self.auto_save_var).grid(row=0, column=2, sticky='w')

        self.start_btn = ttk.Button(ctrl_frame, text='Start Training', command=self.start_training)
        self.start_btn.grid(row=1, column=0, pady=(10,0))

        self.stop_btn = ttk.Button(ctrl_frame, text='Stop', command=self.stop_training, state='disabled')
        self.stop_btn.grid(row=1, column=1, pady=(10,0), sticky='w')

        # progress
        prog_frame = ttk.Frame(main)
        prog_frame.pack(fill='x')
        self.progress = ttk.Progressbar(prog_frame, orient='horizontal', mode='determinate')
        self.progress.pack(fill='x', side='left', expand=True, padx=(0,8))
        self.progress_label = ttk.Label(prog_frame, text='Idle')
        self.progress_label.pack(side='right')

        # logs
        log_frame = ttk.LabelFrame(main, text='Log', padding=8)
        log_frame.pack(fill='both', expand=True)
        self.log = tk.Text(log_frame, height=8, wrap='word')
        self.log.pack(fill='both', expand=True)

        # status bar
        self.status_var = tk.StringVar(value='Ready')
        status = ttk.Label(self, textvariable=self.status_var, relief='sunken', anchor='w', padding=4)
        status.pack(fill='x', side='bottom')

        # internal
        self._training_thread = None
        self._stop_requested = threading.Event()
        self.dataset_path = None

        # try to find dataset
        self.after(100, self._auto_find_dataset)

    def _load_embedded_image(self, size_px=96):
        try:
            raw = base64.b64decode(EMBEDDED_PNG)
            if PIL_AVAILABLE:
                im = Image.open(io.BytesIO(raw))
                im = im.resize((size_px, size_px), Image.LANCZOS)
                tkimg = ImageTk.PhotoImage(im)
                return tkimg
            else:
                # fallback: Tkinter PhotoImage from base64
                return tk.PhotoImage(data=raw)
        except Exception:
            return None

    def _auto_find_dataset(self):
        # prefer the script directory
        script_dir = Path.cwd()
        found = find_dataset_dir(script_dir)
        if not found:
            # try home dir
            found = find_dataset_dir(Path.home())
        if found:
            self.dataset_path = found
            self.dataset_var.set(str(found))
            self.log_message(f"Found dataset at: {found}")
            self.status_var.set('Dataset found')
        else:
            self.dataset_var.set('(dataset not found)')
            self.log_message('Could not find "dataset" folder automatically. Click "Choose another" to pick it.')
            self.status_var.set('Dataset not found')

    def choose_dataset(self):
        folder = filedialog.askdirectory(title='Select dataset folder (folder named dataset preferred)')
        if folder:
            p = Path(folder)
            # if user chose a file inside dataset, allow selecting parent
            if p.is_file():
                p = p.parent
            self.dataset_path = p
            self.dataset_var.set(str(self.dataset_path))
            self.log_message(f'User selected dataset: {self.dataset_path}')
            self.status_var.set('Dataset selected')

    def log_message(self, text):
        t = time.strftime('%H:%M:%S')
        self.log.insert('end', f'[{t}] {text}\n')
        self.log.see('end')

    def start_training(self):
        if self._training_thread and self._training_thread.is_alive():
            messagebox.showwarning('Training', 'Training is already running')
            return
        if not self.dataset_path:
            # as requested, try to avoid asking—still must allow user to pick if not found
            res = messagebox.askyesno('Dataset not found', 'No dataset folder was found automatically. Do you want to choose one now?')
            if res:
                self.choose_dataset()
            else:
                return
        self._stop_requested.clear()
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.progress['value'] = 0
        self.progress_label.config(text='Starting...')
        self.status_var.set('Training...')

        # spawn training thread
        t = threading.Thread(target=self._run_training_thread, daemon=True)
        self._training_thread = t
        t.start()

    def stop_training(self):
        self._stop_requested.set()
        self.log_message('Stop requested — will stop after current step')
        self.status_var.set('Stop requested')

    def _run_training_thread(self):
        try:
            def progress_callback(pct, message):
                # called from training thread — schedule UI update on main thread
                self.after(0, self._update_progress_ui, pct, message)
                if self._stop_requested.is_set():
                    raise KeyboardInterrupt('Training stopped by user')

            # call fake_train; replace this with your real trainer function
            trained_dir = fake_train(self.dataset_path, progress_callback)

            # if auto-save enabled, ensure model metadata saved with user-specified name
            if self.auto_save_var.get():
                model_base = self.model_name.get().strip() or 'model'
                # store a pointer file in trained_dir
                meta = {
                    'saved_as': model_base,
                    'saved_to': str(trained_dir),
                    'completed_at': time.asctime()
                }
                safe_write_json(trained_dir / f'{model_base}_meta.json', meta)

            self.after(0, lambda: messagebox.showinfo('Training', f'Training finished. Outputs saved to:\n{trained_dir}'))
            self.after(0, lambda: self.status_var.set('Idle'))
            self.after(0, lambda: self.start_btn.config(state='normal'))
            self.after(0, lambda: self.stop_btn.config(state='disabled'))
            self.log_message(f'Training finished; outputs: {trained_dir}')
        except KeyboardInterrupt:
            self.after(0, lambda: messagebox.showinfo('Training', 'Training stopped by user'))
            self.after(0, lambda: self.start_btn.config(state='normal'))
            self.after(0, lambda: self.stop_btn.config(state='disabled'))
            self.after(0, lambda: self.status_var.set('Idle'))
            self.log_message('Training stopped by user')
        except Exception as e:
            self.after(0, lambda: messagebox.showerror('Training error', str(e)))
            self.after(0, lambda: self.start_btn.config(state='normal'))
            self.after(0, lambda: self.stop_btn.config(state='disabled'))
            self.after(0, lambda: self.status_var.set('Error'))
            self.log_message(f'Error during training: {e}')

    def _update_progress_ui(self, pct, message):
        self.progress['value'] = pct
        self.progress_label.config(text=f'{pct}% — {message}')
        self.log_message(message)


# ----------------------------- main -----------------------------

def main():
    app = TrainerUI()
    app.mainloop()


if __name__ == '__main__':
    main()

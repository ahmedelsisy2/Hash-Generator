
import hashlib
import sys
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    from tkinter.scrolledtext import ScrolledText
except ImportError:  # pragma: no cover
    tk = None
ALGORITHMS = {
    "MD5":     {"func": hashlib.md5,    "bits": 128, "hex_len": 32},
    "SHA-256": {"func": hashlib.sha256, "bits": 256, "hex_len": 64},
}


def compute_hash(text: str, algorithm: str) -> str:
 
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unsupported algorithm: {algorithm!r}")
    data = text.encode("utf-8")                     
    return ALGORITHMS[algorithm]["func"](data).hexdigest() 


def run_self_tests() -> bool:
    results = []

    def check(name, condition):
        results.append(condition)
        print(f"[{'PASS' if condition else 'FAIL'}] {name}")

    
    for alg in ALGORITHMS:
        check(f"{alg}: same input gives same hash",
              compute_hash("Hello, World!", alg) == compute_hash("Hello, World!", alg))

    
    for alg in ALGORITHMS:
        check(f"{alg}: different input gives different hash",
              compute_hash("hello", alg) != compute_hash("Hello", alg))
    for alg, info in ALGORITHMS.items():
        for sample in ["", "a", "short", "x" * 10_000]:
            check(f"{alg}: length is {info['hex_len']} hex chars for input of "
                  f"{len(sample)} chars",
                  len(compute_hash(sample, alg)) == info["hex_len"])
    md5_len = len(compute_hash("test", "MD5"))
    sha_len = len(compute_hash("test", "SHA-256"))
    check("MD5 = 32 hex chars (128 bits)", md5_len == 32 and md5_len * 4 == 128)
    check("SHA-256 = 64 hex chars (256 bits)", sha_len == 64 and sha_len * 4 == 256)
    check("MD5('hello') known value",
          compute_hash("hello", "MD5") == "5d41402abc4b2a76b9719d911017c592")
    check("SHA-256('hello') known value",
          compute_hash("hello", "SHA-256") ==
          "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824")
    check("MD5('') known value",
          compute_hash("", "MD5") == "d41d8cd98f00b204e9800998ecf8427e")
    special = "Pässwörd 123 !@#$%^&*() 你好 😀\tTab"
    check("UTF-8 / special characters are handled",
          compute_hash(special, "SHA-256") == compute_hash(special, "SHA-256")
          and len(compute_hash(special, "SHA-256")) == 64)
    check("Trailing space changes the hash",
          compute_hash("abc", "MD5") != compute_hash("abc ", "MD5"))
    try:
        compute_hash("x", "SHA-999")
        check("Unsupported algorithm raises ValueError", False)
    except ValueError:
        check("Unsupported algorithm raises ValueError", True)

    ok = all(results)
    print(f"\n{sum(results)}/{len(results)} tests passed.")
    return ok
COLOR_BG = "#f4f6fb"        # window background
COLOR_HEADER = "#1f3a68"    # header bar
COLOR_ACCENT = "#2f6fed"    # primary button
COLOR_ACCENT_DK = "#1f55c4"
COLOR_TEXT = "#1d2433"
COLOR_MUTED = "#5b657a"
COLOR_OK = "#1b7f3b"
COLOR_ERR = "#b3261e"
COLOR_RESULT_BG = "#eef2fa"

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_SUB = ("Segoe UI", 10)
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_BODY = ("Segoe UI", 11)
FONT_MONO = ("Consolas", 12)


class HashGeneratorApp:
    """Main application window."""

    def __init__(self, root: "tk.Tk"):
        self.root = root
        self.root.title("Hash Generator")
        self.root.geometry("760x640")
        self.root.minsize(620, 560)
        self.root.configure(bg=COLOR_BG)

        self.algorithm_var = tk.StringVar(value="SHA-256")
        self.status_var = tk.StringVar(value="Enter some text and click “Generate Hash”.")
        self.info_var = tk.StringVar(value="")

        self._configure_styles()
        self._build_header()
        self._build_body()
        self._build_status_bar()

        self.root.bind("<Control-Return>", lambda _e: self.generate_hash())
        self.input_text.focus_set()

    # ---- styling ---------------------------------------------------------- #
    def _configure_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")  # 'clam' allows custom colours on all platforms

        style.configure("TFrame", background=COLOR_BG)
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT,
                        font=FONT_LABEL)
        style.configure("Info.TLabel", foreground=COLOR_MUTED, font=FONT_SUB)

        style.configure("Primary.TButton", font=FONT_LABEL, padding=(16, 8),
                        background=COLOR_ACCENT, foreground="white", borderwidth=0)
        style.map("Primary.TButton",
                  background=[("active", COLOR_ACCENT_DK)])

        style.configure("Secondary.TButton", font=FONT_LABEL, padding=(16, 8),
                        background="#dfe5f2", foreground=COLOR_TEXT, borderwidth=0)
        style.map("Secondary.TButton",
                  background=[("active", "#cbd4e8")])

        style.configure("TCombobox", padding=5, font=FONT_BODY)
        # Larger font for the dropdown list itself.
        self.root.option_add("*TCombobox*Listbox.font", FONT_BODY)

    # ---- layout ----------------------------------------------------------- #
    def _build_header(self):
        header = tk.Frame(self.root, bg=COLOR_HEADER)
        header.pack(fill="x")
        tk.Label(header, text="Hash Generator", font=FONT_TITLE,
                 bg=COLOR_HEADER, fg="white").pack(anchor="w", padx=24, pady=(16, 0))
        tk.Label(header,
                 text="Convert any text into a fixed-length digest using MD5 or SHA-256",
                 font=FONT_SUB, bg=COLOR_HEADER, fg="#c9d6f2"
                 ).pack(anchor="w", padx=24, pady=(0, 16))

    def _build_body(self):
        body = ttk.Frame(self.root, padding=(24, 16, 24, 8))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=2)   # input area grows
        body.rowconfigure(6, weight=1)   # result area grows

        # --- Input text area ---
        ttk.Label(body, text="1. Enter your text").grid(row=0, column=0, sticky="w")
        self.input_text = ScrolledText(
            body, height=7, wrap="word", font=FONT_BODY, relief="flat",
            bg="white", fg=COLOR_TEXT, insertbackground=COLOR_TEXT,
            highlightthickness=1, highlightbackground="#c5cce0",
            highlightcolor=COLOR_ACCENT, padx=8, pady=8)
        self.input_text.grid(row=1, column=0, sticky="nsew", pady=(4, 12))

        # --- Algorithm selection ---
        ttk.Label(body, text="2. Choose a hashing algorithm").grid(row=2, column=0, sticky="w")
        self.algorithm_box = ttk.Combobox(
            body, textvariable=self.algorithm_var, values=list(ALGORITHMS.keys()),
            state="readonly", font=FONT_BODY, width=18)
        self.algorithm_box.grid(row=3, column=0, sticky="w", pady=(4, 12))
        # Refresh info text when the algorithm changes.
        self.algorithm_box.bind("<<ComboboxSelected>>", self._on_algorithm_change)

        # --- Buttons ---
        buttons = ttk.Frame(body)
        buttons.grid(row=4, column=0, sticky="w", pady=(0, 14))
        ttk.Button(buttons, text="Generate Hash", style="Primary.TButton",
                   command=self.generate_hash).pack(side="left")
        ttk.Button(buttons, text="Copy Hash", style="Secondary.TButton",
                   command=self.copy_hash).pack(side="left", padx=10)
        ttk.Button(buttons, text="Clear", style="Secondary.TButton",
                   command=self.clear_all).pack(side="left")

        # --- Result area ---
        ttk.Label(body, text="3. Resulting hash (hexadecimal)").grid(row=5, column=0, sticky="w")
        self.result_text = tk.Text(
            body, height=3, wrap="char", font=FONT_MONO, relief="flat",
            bg=COLOR_RESULT_BG, fg=COLOR_TEXT, highlightthickness=1,
            highlightbackground="#c5cce0", padx=8, pady=8, state="disabled")
        self.result_text.grid(row=6, column=0, sticky="nsew", pady=(4, 6))

        ttk.Label(body, textvariable=self.info_var, style="Info.TLabel"
                  ).grid(row=7, column=0, sticky="w")

    def _build_status_bar(self):
        self.status_label = tk.Label(
            self.root, textvariable=self.status_var, anchor="w", font=FONT_SUB,
            bg="#e3e8f4", fg=COLOR_MUTED, padx=24, pady=6)
        self.status_label.pack(fill="x", side="bottom")

    # ---- helpers ---------------------------------------------------------- #
    def _set_status(self, message: str, kind: str = "info"):
        """Show a message in the status bar; colour depends on `kind`."""
        colors = {"info": COLOR_MUTED, "ok": COLOR_OK, "error": COLOR_ERR}
        self.status_label.configure(fg=colors.get(kind, COLOR_MUTED))
        self.status_var.set(message)

    def _set_result(self, value: str):
        """Write text into the (read-only) result box."""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", value)
        self.result_text.configure(state="disabled")

    def _get_result(self) -> str:
        return self.result_text.get("1.0", "end-1c").strip()

    def _on_algorithm_change(self, _event=None):
        """Clear the old hash so a result is never shown with the wrong algorithm."""
        self._set_result("")
        self.info_var.set("")
        self._set_status(f"{self.algorithm_var.get()} selected. Click “Generate Hash”.")

    # ---- button handlers -------------------------------------------------- #
    def generate_hash(self):
        """Read the input, hash it with the chosen algorithm, show the result."""
        text = self.input_text.get("1.0", "end-1c")
        algorithm = self.algorithm_var.get()
        if text == "":
            self._set_result("")
            self.info_var.set("")
            self._set_status("Please enter some text before generating a hash.", "error")
            messagebox.showwarning("Empty input",
                                   "The text box is empty.\nPlease type some text to hash.")
            self.input_text.focus_set()
            return

        try:
            digest = compute_hash(text, algorithm)
        except Exception as exc:  # unexpected problem (e.g. bad algorithm name)
            self._set_status(f"Error while hashing: {exc}", "error")
            messagebox.showerror("Hashing error", str(exc))
            return

        info = ALGORITHMS[algorithm]
        self._set_result(digest)
        self.info_var.set(
            f"{algorithm}  •  {info['bits']}-bit digest  •  {len(digest)} hex characters  "
            f"•  input: {len(text.encode('utf-8'))} byte(s)")
        self._set_status("Hash generated successfully.", "ok")

    def copy_hash(self):
        """Copy the displayed hash to the system clipboard."""
        digest = self._get_result()
        if not digest:
            self._set_status("Nothing to copy. Generate a hash first.", "error")
            messagebox.showinfo("Nothing to copy", "Generate a hash first, then copy it.")
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(digest)
            self.root.update()  # keeps the clipboard content after the app closes
            self._set_status("Hash copied to clipboard.", "ok")
        except tk.TclError as exc:
            self._set_status(f"Could not access the clipboard: {exc}", "error")

    def clear_all(self):
        """Reset the input, result and messages."""
        self.input_text.delete("1.0", "end")
        self._set_result("")
        self.info_var.set("")
        self._set_status("Cleared. Enter some text and click “Generate Hash”.")
        self.input_text.focus_set()


def main():
    if "--test" in sys.argv:
        sys.exit(0 if run_self_tests() else 1)
    if tk is None:
        sys.exit("Tkinter is not available. Reinstall Python from python.org "
                 "and make sure 'tcl/tk and IDLE' is ticked.")
    root = tk.Tk()
    HashGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

"""
╔══════════════════════════════════════════════════════════════════╗
║              TASK MANAGER — DESKTOP EDITION                      ║
║              A fully standalone, high-quality GUI                ║
║              Built with Python + Tkinter only                    ║
╚══════════════════════════════════════════════════════════════════╝

HOW TO RUN:
    python task_manager_gui.py

REQUIREMENTS:
    Python 3.8+  (Tkinter is included — no pip installs needed)

FEATURES:
    ✅  Add / Edit / Delete tasks
    ✅  Mark Complete / Incomplete
    ✅  Priority levels  (High / Medium / Low)
    ✅  Due dates with overdue detection
    ✅  Search, Filter, Sort
    ✅  Statistics window with progress bar
    ✅  Export to timestamped .txt file
    ✅  Keyboard shortcuts
    ✅  Colour-coded rows
    ✅  Persistent storage in tasks.txt
"""

import os
import datetime
import tkinter as tk
from tkinter import messagebox, ttk


# ══════════════════════════════════════════════════════════════════
#  SECTION 1 — CONSTANTS & THEME
#  All colours, fonts, and sizes live here.
#  Change one value and the whole app updates consistently.
# ══════════════════════════════════════════════════════════════════

TASKS_FILE = "tasks.txt"

# ── Colour Palette ────────────────────────────────────────────────
BG_DARK      = "#1A1D27"   # main window background
BG_PANEL     = "#22263A"   # sidebar / toolbar background
BG_CARD      = "#2C3050"   # card / input background
BG_HOVER     = "#353A5E"   # button hover state
ACCENT_BLUE  = "#4F8EF7"   # primary accent — buttons, highlights
ACCENT_GREEN = "#3DD68C"   # success / complete
ACCENT_AMBER = "#F5A623"   # warning / medium priority
ACCENT_RED   = "#F75F5F"   # danger / high priority / overdue
ACCENT_GREY  = "#8892B0"   # muted text / low priority
TEXT_PRIMARY = "#E8EAF6"   # main text
TEXT_MUTED   = "#8892B0"   # secondary / label text
ROW_DONE     = "#1E3A2F"   # completed row background
ROW_ODD      = "#22263A"   # alternating row
ROW_EVEN     = "#1E2138"   # alternating row
ROW_OVERDUE  = "#3A1E1E"   # overdue row background
BORDER       = "#3A3F5C"   # subtle borders

# ── Typography ────────────────────────────────────────────────────
FONT_TITLE   = ("Georgia",          20, "bold")
FONT_HEADING = ("Courier New",      11, "bold")
FONT_BODY    = ("Courier New",      10)
FONT_SMALL   = ("Courier New",       9)
FONT_BTN     = ("Courier New",      10, "bold")
FONT_MONO    = ("Courier New",      10)

# ── Priority metadata ─────────────────────────────────────────────
PRIORITY_CONFIG = {
    "High":   {"colour": ACCENT_RED,   "symbol": "▲", "sort_key": 0},
    "Medium": {"colour": ACCENT_AMBER, "symbol": "●", "sort_key": 1},
    "Low":    {"colour": ACCENT_GREY,  "symbol": "▼", "sort_key": 2},
}


# ══════════════════════════════════════════════════════════════════
#  SECTION 2 — CORE DATA / LOGIC LAYER
#  Pure functions — no UI, no Tkinter imports used here.
#  These could be imported by a CLI or another front-end unchanged.
# ══════════════════════════════════════════════════════════════════

def load_tasks() -> list[str]:
    """Read tasks.txt and return a list of raw task strings."""
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip()]


def save_tasks(tasks: list[str]) -> None:
    """Write the full task list to tasks.txt, overwriting previous content."""
    with open(TASKS_FILE, "w", encoding="utf-8") as fh:
        for task in tasks:
            fh.write(task + "\n")


def parse_task(raw: str) -> dict:
    """
    Convert a raw pipe-delimited task string into a structured dictionary.

    Expected format:  "[ ] | High | 2025-12-31 | Buy groceries"
    Returns a dict:   {status, priority, due, name, is_complete, is_overdue}
    """
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) == 4:
        status, priority, due, name = parts
    else:
        # Gracefully handle old-format or malformed tasks
        status, priority, due, name = "[ ]", "Medium", "No due date", raw

    is_complete = "[X]" in status
    is_overdue  = False

    if not is_complete and due != "No due date":
        try:
            due_dt     = datetime.datetime.strptime(due, "%Y-%m-%d").date()
            is_overdue = due_dt < datetime.date.today()
        except ValueError:
            pass  # Ignore unparseable dates silently

    return {
        "status":      status,
        "priority":    priority,
        "due":         due,
        "name":        name,
        "is_complete": is_complete,
        "is_overdue":  is_overdue,
    }


def build_task_string(status: str, priority: str, due: str, name: str) -> str:
    """Assemble the canonical pipe-delimited string stored in tasks.txt."""
    return f"{status} | {priority} | {due} | {name}"


def compute_stats(tasks: list[str]) -> dict:
    """Return a dict of statistics derived from the task list."""
    parsed    = [parse_task(t) for t in tasks]
    total     = len(parsed)
    completed = sum(1 for p in parsed if p["is_complete"])
    overdue   = sum(1 for p in parsed if p["is_overdue"])
    by_prio   = {k: sum(1 for p in parsed if p["priority"] == k)
                 for k in ("High", "Medium", "Low")}
    percent   = (completed / total * 100) if total else 0.0
    return {
        "total":     total,
        "completed": completed,
        "remaining": total - completed,
        "overdue":   overdue,
        "percent":   percent,
        "by_prio":   by_prio,
    }


def export_to_file(tasks: list[str]) -> str:
    """Write a formatted export file and return its filename."""
    stamp    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tasks_export_{stamp}.txt"
    stats    = compute_stats(tasks)
    sep      = "═" * 70

    with open(filename, "w", encoding="utf-8") as fh:
        fh.write(f"TASK MANAGER — EXPORT\n")
        fh.write(f"Generated : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        fh.write(f"{sep}\n")
        fh.write(f"{'#':<5} {'STATUS':<8} {'PRIORITY':<10} {'DUE DATE':<14} TASK\n")
        fh.write(f"{sep}\n")
        for i, task in enumerate(tasks, 1):
            p = parse_task(task)
            status_lbl = "DONE   " if p["is_complete"] else "PENDING"
            overdue    = " ⚠ OVERDUE" if p["is_overdue"] else ""
            fh.write(
                f"{i:<5} {status_lbl:<8} {p['priority']:<10} "
                f"{p['due']:<14} {p['name']}{overdue}\n"
            )
        fh.write(f"{sep}\n")
        fh.write(
            f"Total: {stats['total']}  |  "
            f"Completed: {stats['completed']}  |  "
            f"Remaining: {stats['remaining']}  |  "
            f"Overdue: {stats['overdue']}\n"
        )
    return filename


# ══════════════════════════════════════════════════════════════════
#  SECTION 3 — REUSABLE UI PRIMITIVES
#  Small helper widgets used across the application.
# ══════════════════════════════════════════════════════════════════

def _style_button(btn: tk.Button,
                  bg: str = BG_CARD,
                  fg: str = TEXT_PRIMARY,
                  hover_bg: str = BG_HOVER) -> None:
    """Apply consistent dark-theme styling to a tk.Button and wire hover effects."""
    btn.configure(
        bg=bg, fg=fg,
        activebackground=hover_bg, activeforeground=TEXT_PRIMARY,
        relief="flat", bd=0,
        cursor="hand2",
        font=FONT_BTN,
        padx=12, pady=6,
    )
    btn.bind("<Enter>", lambda _: btn.configure(bg=hover_bg))
    btn.bind("<Leave>", lambda _: btn.configure(bg=bg))


def _make_label(parent, text: str, font=FONT_BODY,
                fg: str = TEXT_MUTED, **kwargs) -> tk.Label:
    """Convenience wrapper — creates a styled Label with dark background."""
    return tk.Label(parent, text=text, font=font, fg=fg,
                    bg=parent.cget("bg"), **kwargs)


def _make_entry(parent, textvariable: tk.StringVar, width: int = 30) -> tk.Entry:
    """Convenience wrapper — creates a styled Entry widget."""
    return tk.Entry(
        parent,
        textvariable=textvariable,
        font=FONT_MONO,
        bg=BG_DARK,
        fg=TEXT_PRIMARY,
        insertbackground=TEXT_PRIMARY,
        relief="flat",
        bd=4,
        width=width,
    )


# ══════════════════════════════════════════════════════════════════
#  SECTION 4 — TASK DIALOG  (Add / Edit popup)
# ══════════════════════════════════════════════════════════════════

class TaskDialog(tk.Toplevel):
    """
    Modal dialog for creating or editing a single task.

    Parameters
    ----------
    parent       : the root or any Tk widget
    title        : window title bar text
    initial_data : dict with keys name/priority/due when editing,
                   None when adding a new task
    """

    def __init__(self, parent: tk.Widget, title: str,
                 initial_data: dict | None = None):
        super().__init__(parent)

        self.result: dict | None = None  # Set to a dict on Save, stays None on Cancel

        # ── Window setup ──────────────────────────────────────────
        self.title(title)
        self.configure(bg=BG_PANEL)
        self.resizable(False, False)
        self.grab_set()                   # Block interaction with the parent window

        # ── State variables ───────────────────────────────────────
        self._name_var     = tk.StringVar()
        self._priority_var = tk.StringVar(value="Medium")
        self._due_var      = tk.StringVar(value="")

        if initial_data:
            self._name_var.set(initial_data.get("name", ""))
            self._priority_var.set(initial_data.get("priority", "Medium"))
            due = initial_data.get("due", "")
            self._due_var.set("" if due == "No due date" else due)

        # ── Build layout ──────────────────────────────────────────
        self._build_ui()
        self._center_on(parent)

        # Hand control back to Tkinter — wait until this window is destroyed
        self.wait_window(self)

    # ── Layout builder ────────────────────────────────────────────
    def _build_ui(self) -> None:
        outer = tk.Frame(self, bg=BG_PANEL, padx=28, pady=24)
        outer.pack(fill="both", expand=True)

        # Title strip
        tk.Label(outer, text="TASK DETAILS", font=FONT_HEADING,
                 fg=ACCENT_BLUE, bg=BG_PANEL).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        # ── Task Name ─────────────────────────────────────────────
        _make_label(outer, "Task Name").grid(row=1, column=0, sticky="w", pady=4)
        name_entry = _make_entry(outer, self._name_var, width=34)
        name_entry.grid(row=1, column=1, sticky="ew", pady=4, padx=(10, 0))
        name_entry.focus_set()            # Put the cursor in this field immediately

        # ── Priority ──────────────────────────────────────────────
        _make_label(outer, "Priority").grid(row=2, column=0, sticky="w", pady=4)
        prio_frame = tk.Frame(outer, bg=BG_PANEL)
        prio_frame.grid(row=2, column=1, sticky="w", pady=4, padx=(10, 0))

        for prio, cfg in PRIORITY_CONFIG.items():
            rb = tk.Radiobutton(
                prio_frame,
                text=f" {cfg['symbol']} {prio}",
                variable=self._priority_var,
                value=prio,
                font=FONT_BODY,
                fg=cfg["colour"],
                bg=BG_PANEL,
                activebackground=BG_PANEL,
                selectcolor=BG_DARK,
                cursor="hand2",
            )
            rb.pack(side="left", padx=(0, 14))

        # ── Due Date ──────────────────────────────────────────────
        _make_label(outer, "Due Date").grid(row=3, column=0, sticky="w", pady=4)
        due_frame = tk.Frame(outer, bg=BG_PANEL)
        due_frame.grid(row=3, column=1, sticky="w", pady=4, padx=(10, 0))

        _make_entry(due_frame, self._due_var, width=16).pack(side="left")
        _make_label(due_frame, "  YYYY-MM-DD  or leave blank",
                    font=FONT_SMALL).pack(side="left")

        # ── Divider ───────────────────────────────────────────────
        tk.Frame(outer, height=1, bg=BORDER).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=18)

        # ── Buttons ───────────────────────────────────────────────
        btn_frame = tk.Frame(outer, bg=BG_PANEL)
        btn_frame.grid(row=5, column=0, columnspan=2, sticky="e")

        cancel_btn = tk.Button(btn_frame, text="Cancel", command=self.destroy)
        _style_button(cancel_btn)
        cancel_btn.pack(side="left", padx=(0, 8))

        save_btn = tk.Button(btn_frame, text="Save Task", command=self._on_save)
        _style_button(save_btn, bg=ACCENT_BLUE, fg="#FFFFFF", hover_bg="#6DA3F8")
        save_btn.pack(side="left")

        # Enter key triggers Save
        self.bind("<Return>", lambda _: self._on_save())
        self.bind("<Escape>", lambda _: self.destroy())

    # ── Action ────────────────────────────────────────────────────
    def _on_save(self) -> None:
        name = self._name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name",
                                   "Task name cannot be empty.", parent=self)
            return

        due_raw = self._due_var.get().strip()
        if due_raw:
            try:
                datetime.datetime.strptime(due_raw, "%Y-%m-%d")
                due = due_raw
            except ValueError:
                messagebox.showwarning(
                    "Invalid Date",
                    "Use YYYY-MM-DD format (e.g. 2025-12-31).", parent=self)
                return
        else:
            due = "No due date"

        self.result = {
            "name":     name,
            "priority": self._priority_var.get(),
            "due":      due,
        }
        self.destroy()

    # ── Utility ───────────────────────────────────────────────────
    def _center_on(self, parent: tk.Widget) -> None:
        self.update_idletasks()
        pw = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w  = self.winfo_width()
        h  = self.winfo_height()
        x  = pw + (parent.winfo_width()  - w) // 2
        y  = py + (parent.winfo_height() - h) // 2
        self.geometry(f"+{x}+{y}")


# ══════════════════════════════════════════════════════════════════
#  SECTION 5 — STATISTICS WINDOW
# ══════════════════════════════════════════════════════════════════

class StatsWindow(tk.Toplevel):
    """Pop-up window showing computed statistics about the task list."""

    def __init__(self, parent: tk.Widget, tasks: list[str]):
        super().__init__(parent)
        self.title("Statistics")
        self.configure(bg=BG_PANEL)
        self.resizable(False, False)
        self.grab_set()

        stats = compute_stats(tasks)
        self._build_ui(stats)
        self._center_on(parent)

    def _build_ui(self, s: dict) -> None:
        outer = tk.Frame(self, bg=BG_PANEL, padx=32, pady=24)
        outer.pack(fill="both", expand=True)

        tk.Label(outer, text="TASK STATISTICS", font=FONT_HEADING,
                 fg=ACCENT_BLUE, bg=BG_PANEL).pack(anchor="w", pady=(0, 16))

        # ── Progress bar ──────────────────────────────────────────
        tk.Label(outer, text=f"Overall Progress — {s['percent']:.1f}% complete",
                 font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_PANEL).pack(anchor="w")

        bar_frame = tk.Frame(outer, bg=BG_DARK, height=14,
                             highlightbackground=BORDER, highlightthickness=1)
        bar_frame.pack(fill="x", pady=(4, 16))
        bar_frame.update_idletasks()

        filled_w = int(bar_frame.winfo_width() * s["percent"] / 100)
        if filled_w > 0:
            tk.Frame(bar_frame, bg=ACCENT_GREEN, height=14,
                     width=filled_w).pack(side="left")

        # ── Stat rows ─────────────────────────────────────────────
        rows = [
            ("Total Tasks",       s["total"],           TEXT_PRIMARY),
            ("Completed",         s["completed"],        ACCENT_GREEN),
            ("Remaining",         s["remaining"],        ACCENT_AMBER),
            ("Overdue",           s["overdue"],          ACCENT_RED),
            ("── By Priority ──", "",                    TEXT_MUTED),
            ("  High",            s["by_prio"]["High"],  ACCENT_RED),
            ("  Medium",          s["by_prio"]["Medium"],ACCENT_AMBER),
            ("  Low",             s["by_prio"]["Low"],   ACCENT_GREY),
        ]

        for label, value, colour in rows:
            row_frame = tk.Frame(outer, bg=BG_PANEL)
            row_frame.pack(fill="x", pady=2)
            tk.Label(row_frame, text=label, font=FONT_BODY,
                     fg=TEXT_MUTED, bg=BG_PANEL, width=20, anchor="w").pack(side="left")
            if value != "":
                tk.Label(row_frame, text=str(value), font=FONT_BODY,
                         fg=colour, bg=BG_PANEL, anchor="w").pack(side="left")

        tk.Frame(outer, height=1, bg=BORDER).pack(fill="x", pady=14)

        close_btn = tk.Button(outer, text="Close", command=self.destroy)
        _style_button(close_btn, bg=ACCENT_BLUE, fg="#FFFFFF", hover_bg="#6DA3F8")
        close_btn.pack(anchor="e")
        self.bind("<Escape>", lambda _: self.destroy())

    def _center_on(self, parent: tk.Widget) -> None:
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width()  - self.winfo_width())  // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")


# ══════════════════════════════════════════════════════════════════
#  SECTION 6 — MAIN APPLICATION WINDOW
# ══════════════════════════════════════════════════════════════════

class TaskManagerApp:
    """
    Root application controller.

    Builds the main window, manages self.tasks as the single source
    of truth, and connects every UI action to the data layer.
    """

    def __init__(self, root: tk.Tk):
        self.root   = root
        self.tasks  = load_tasks()

        # ── Filter / sort state ───────────────────────────────────
        self.search_var   = tk.StringVar()
        self.status_var   = tk.StringVar(value="All")
        self.priority_var = tk.StringVar(value="All")
        self.sort_var     = tk.StringVar(value="Default")

        # Watch for changes in every filter control
        for var in (self.search_var, self.status_var,
                    self.priority_var, self.sort_var):
            var.trace_add("write", self._on_filter_change)

        # ── Build UI sections ─────────────────────────────────────
        self._configure_window()
        self._apply_ttk_style()
        self._build_header()
        self._build_toolbar()
        self._build_filter_bar()
        self._build_task_table()
        self._build_status_bar()
        self._bind_keyboard_shortcuts()

        self.refresh_table()

    # ──────────────────────────────────────────────────────────────
    #  WINDOW & STYLE SETUP
    # ──────────────────────────────────────────────────────────────

    def _configure_window(self) -> None:
        self.root.title("Task Manager")
        self.root.geometry("960x620")
        self.root.minsize(720, 480)
        self.root.configure(bg=BG_DARK)
        # Make column 0 of the root grid expand with the window
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(3, weight=1)    # Task table row stretches

    def _apply_ttk_style(self) -> None:
        """Configure ttk.Treeview colours — ttk widgets need a Style object."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview",
                        background=ROW_EVEN,
                        foreground=TEXT_PRIMARY,
                        rowheight=28,
                        fieldbackground=ROW_EVEN,
                        font=FONT_BODY,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=BG_PANEL,
                        foreground=ACCENT_BLUE,
                        font=FONT_HEADING,
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", BG_HOVER)],
                  foreground=[("selected", TEXT_PRIMARY)])
        style.map("Treeview.Heading",
                  background=[("active", BG_HOVER)])

        style.configure("Vertical.TScrollbar",
                        background=BG_PANEL,
                        troughcolor=BG_DARK,
                        borderwidth=0,
                        arrowcolor=TEXT_MUTED)

    # ──────────────────────────────────────────────────────────────
    #  HEADER  (app title + live clock)
    # ──────────────────────────────────────────────────────────────

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=BG_PANEL, pady=10)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        tk.Label(header, text="◈ TASK MANAGER", font=FONT_TITLE,
                 fg=ACCENT_BLUE, bg=BG_PANEL, padx=20).grid(
            row=0, column=0, sticky="w")

        self._clock_var = tk.StringVar()
        tk.Label(header, textvariable=self._clock_var, font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_PANEL, padx=20).grid(
            row=0, column=2, sticky="e")

        self._tick_clock()   # Start the live clock

    def _tick_clock(self) -> None:
        """Update the header clock every second using Tkinter's after() scheduler."""
        now = datetime.datetime.now().strftime("%A, %d %b %Y  ·  %H:%M:%S")
        self._clock_var.set(now)
        # Schedule this same function to run again in 1000 ms (1 second)
        self.root.after(1000, self._tick_clock)

    # ──────────────────────────────────────────────────────────────
    #  TOOLBAR  (action buttons)
    # ──────────────────────────────────────────────────────────────

    def _build_toolbar(self) -> None:
        toolbar = tk.Frame(self.root, bg=BG_PANEL, pady=6, padx=10)
        toolbar.grid(row=1, column=0, sticky="ew")

        # (label, action, bg_colour)
        btn_defs = [
            ("➕  Add",              self.cmd_add,             ACCENT_BLUE),
            ("✏️  Edit",             self.cmd_edit,            BG_CARD),
            ("🗑️  Delete",           self.cmd_delete,          BG_CARD),
            ("✅  Complete",         self.cmd_mark_complete,   BG_CARD),
            ("↩️  Incomplete",       self.cmd_mark_incomplete, BG_CARD),
            ("📊  Stats",            self.cmd_stats,           BG_CARD),
            ("💾  Export",           self.cmd_export,          BG_CARD),
            ("❌  Exit",             self.root.destroy,        BG_CARD),
        ]

        for label, action, colour in btn_defs:
            btn = tk.Button(toolbar, text=label, command=action)
            hover = "#6DA3F8" if colour == ACCENT_BLUE else BG_HOVER
            _style_button(btn, bg=colour, hover_bg=hover)
            btn.pack(side="left", padx=3)

    # ──────────────────────────────────────────────────────────────
    #  FILTER BAR  (search + dropdowns)
    # ──────────────────────────────────────────────────────────────

    def _build_filter_bar(self) -> None:
        bar = tk.Frame(self.root, bg=BG_DARK, pady=6, padx=10)
        bar.grid(row=2, column=0, sticky="ew")

        def dropdown(parent, label: str, var: tk.StringVar,
                     options: list[str]) -> None:
            tk.Label(parent, text=label, font=FONT_SMALL,
                     fg=TEXT_MUTED, bg=BG_DARK).pack(side="left")
            menu = tk.OptionMenu(parent, var, *options)
            menu.config(font=FONT_SMALL, bg=BG_CARD, fg=TEXT_PRIMARY,
                        activebackground=BG_HOVER, activeforeground=TEXT_PRIMARY,
                        highlightthickness=0, relief="flat", cursor="hand2",
                        width=10)
            menu["menu"].config(bg=BG_CARD, fg=TEXT_PRIMARY,
                                activebackground=BG_HOVER,
                                activeforeground=TEXT_PRIMARY,
                                font=FONT_SMALL)
            menu.pack(side="left", padx=(2, 14))

        # Search box
        tk.Label(bar, text="🔍", font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_DARK).pack(side="left")
        search_entry = _make_entry(bar, self.search_var, width=22)
        search_entry.pack(side="left", padx=(2, 14))

        dropdown(bar, "Status:",   self.status_var,
                 ["All", "Incomplete", "Complete"])
        dropdown(bar, "Priority:", self.priority_var,
                 ["All", "High", "Medium", "Low"])
        dropdown(bar, "Sort by:",  self.sort_var,
                 ["Default", "Priority ▲", "Status", "Name A–Z", "Due Date"])

        # Clear filters button
        clr = tk.Button(bar, text="✕ Clear", command=self._clear_filters)
        _style_button(clr, fg=TEXT_MUTED)
        clr.pack(side="left")

    def _clear_filters(self) -> None:
        self.search_var.set("")
        self.status_var.set("All")
        self.priority_var.set("All")
        self.sort_var.set("Default")

    # ──────────────────────────────────────────────────────────────
    #  TASK TABLE  (Treeview)
    # ──────────────────────────────────────────────────────────────

    def _build_task_table(self) -> None:
        frame = tk.Frame(self.root, bg=BG_DARK)
        frame.grid(row=3, column=0, sticky="nsew", padx=6, pady=(4, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        cols = ("idx", "status", "priority", "due", "name")
        self.tree = ttk.Treeview(frame, columns=cols,
                                 show="headings", selectmode="browse")

        # Column configuration
        col_cfg = [
            ("idx",      "#",          50,  "center"),
            ("status",   "Status",     100, "center"),
            ("priority", "Priority",   90,  "center"),
            ("due",      "Due Date",   110, "center"),
            ("name",     "Task Name",  0,   "w"),    # 0 = stretch
        ]
        for col_id, heading, width, anchor in col_cfg:
            self.tree.heading(col_id, text=heading,
                              command=lambda c=col_id: self._on_heading_click(c))
            if width:
                self.tree.column(col_id, width=width, minwidth=width,
                                 stretch=False, anchor=anchor)
            else:
                self.tree.column(col_id, stretch=True, anchor=anchor, minwidth=180)

        # Row tag colours
        self.tree.tag_configure("complete",   background=ROW_DONE,    foreground="#9ECEAB")
        self.tree.tag_configure("overdue",    background=ROW_OVERDUE, foreground="#F89191")
        self.tree.tag_configure("odd",        background=ROW_ODD)
        self.tree.tag_configure("even",       background=ROW_EVEN)

        scrollbar = ttk.Scrollbar(frame, orient="vertical",
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Double-click to edit
        self.tree.bind("<Double-1>", lambda _: self.cmd_edit())

    # ──────────────────────────────────────────────────────────────
    #  STATUS BAR
    # ──────────────────────────────────────────────────────────────

    def _build_status_bar(self) -> None:
        bar = tk.Frame(self.root, bg=BG_PANEL, pady=4)
        bar.grid(row=4, column=0, sticky="ew")

        self._statusbar_var = tk.StringVar(value="Ready")
        tk.Label(bar, textvariable=self._statusbar_var, font=FONT_SMALL,
                 fg=TEXT_MUTED, bg=BG_PANEL, anchor="w",
                 padx=10).pack(side="left", fill="x", expand=True)

        # Shortcuts hint on the right
        tk.Label(bar, text="A=Add  E=Edit  D=Delete  C=Complete  Ctrl+F=Search",
                 font=FONT_SMALL, fg=BORDER, bg=BG_PANEL, padx=10).pack(side="right")

    def _set_status(self, msg: str) -> None:
        self._statusbar_var.set(msg)

    # ──────────────────────────────────────────────────────────────
    #  KEYBOARD SHORTCUTS
    # ──────────────────────────────────────────────────────────────

    def _bind_keyboard_shortcuts(self) -> None:
        bindings = {
            "a":         self.cmd_add,
            "e":         self.cmd_edit,
            "d":         self.cmd_delete,
            "c":         self.cmd_mark_complete,
            "i":         self.cmd_mark_incomplete,
            "<Delete>":  self.cmd_delete,
            "<F5>":      self.refresh_table,
            "<Escape>":  self._clear_filters,
        }
        for key, func in bindings.items():
            self.root.bind(key, lambda _, f=func: f())

        # Ctrl+F focuses the search box
        self.root.bind("<Control-f>",
                       lambda _: self.search_var.set("") or
                                 self.root.focus_get())

    # ──────────────────────────────────────────────────────────────
    #  REFRESH — the single function that redraws the entire table
    # ──────────────────────────────────────────────────────────────

    def refresh_table(self, *_args) -> None:
        """
        Wipe and redraw every row in the Treeview to match
        the current self.tasks list and active filters.
        Called after every data change and filter control update.
        """
        # 1. Clear all existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # 2. Read filter/sort state
        keyword    = self.search_var.get().strip().lower()
        status_f   = self.status_var.get()
        priority_f = self.priority_var.get()
        sort_by    = self.sort_var.get()

        # 3. Build working list: (original_index, parsed_dict)
        working = [(i, parse_task(t)) for i, t in enumerate(self.tasks)]

        # 4. Apply filters
        if keyword:
            working = [(i, p) for i, p in working
                       if keyword in p["name"].lower()
                       or keyword in p["due"].lower()]
        if status_f == "Complete":
            working = [(i, p) for i, p in working if p["is_complete"]]
        elif status_f == "Incomplete":
            working = [(i, p) for i, p in working if not p["is_complete"]]
        if priority_f != "All":
            working = [(i, p) for i, p in working if p["priority"] == priority_f]

        # 5. Apply sort
        prio_key = lambda x: PRIORITY_CONFIG.get(x[1]["priority"],
                                                  {"sort_key": 9})["sort_key"]
        if sort_by == "Priority ▲":
            working.sort(key=prio_key)
        elif sort_by == "Status":
            working.sort(key=lambda x: 0 if not x[1]["is_complete"] else 1)
        elif sort_by == "Name A–Z":
            working.sort(key=lambda x: x[1]["name"].lower())
        elif sort_by == "Due Date":
            def due_sort_key(x):
                d = x[1]["due"]
                if d == "No due date":
                    return "9999-99-99"
                return d
            working.sort(key=due_sort_key)

        # 6. Insert rows into the Treeview
        for row_num, (original_idx, p) in enumerate(working):
            status_lbl   = "✅  Done"    if p["is_complete"] else "⬜  Pending"
            overdue_mark = " ⚠"          if p["is_overdue"]  else ""
            prio_cfg     = PRIORITY_CONFIG.get(p["priority"], {})
            prio_lbl     = f"{prio_cfg.get('symbol', '')}  {p['priority']}"

            # Pick the row colour tag
            if p["is_complete"]:
                tag = "complete"
            elif p["is_overdue"]:
                tag = "overdue"
            elif row_num % 2 == 0:
                tag = "even"
            else:
                tag = "odd"

            self.tree.insert(
                "", "end",
                iid=str(original_idx),          # Use the real index as the row ID
                values=(
                    original_idx + 1,
                    status_lbl,
                    prio_lbl,
                    p["due"] + overdue_mark,
                    p["name"],
                ),
                tags=(tag,),
            )

        # 7. Update status bar
        total     = len(self.tasks)
        completed = sum(1 for t in self.tasks if "[X]" in t)
        showing   = len(working)
        self._set_status(
            f"Showing {showing} of {total}  │  "
            f"✅ {completed} done  │  "
            f"⬜ {total - completed} remaining"
            + (f"  │  🔍 filtered" if showing < total else "")
        )

    def _on_filter_change(self, *_) -> None:
        self.refresh_table()

    def _on_heading_click(self, col_id: str) -> None:
        """Clicking a column header sets the matching sort mode."""
        mapping = {
            "priority": "Priority ▲",
            "status":   "Status",
            "name":     "Name A–Z",
            "due":      "Due Date",
        }
        if col_id in mapping:
            self.sort_var.set(mapping[col_id])

    # ──────────────────────────────────────────────────────────────
    #  SELECTION HELPER
    # ──────────────────────────────────────────────────────────────

    def _selected_index(self) -> int | None:
        """
        Return the index into self.tasks for the currently selected row.
        Shows a warning and returns None if nothing is selected.
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection",
                                   "Please click on a task first.")
            return None
        # The row iid was set to the original index string in refresh_table
        return int(sel[0])

    # ──────────────────────────────────────────────────────────────
    #  COMMAND HANDLERS  (wired to toolbar buttons + keyboard)
    # ──────────────────────────────────────────────────────────────

    def cmd_add(self) -> None:
        dlg = TaskDialog(self.root, "Add New Task")
        if dlg.result:
            new_task = build_task_string(
                "[ ]",
                dlg.result["priority"],
                dlg.result["due"],
                dlg.result["name"],
            )
            self.tasks.append(new_task)
            save_tasks(self.tasks)
            self.refresh_table()
            self._set_status(f"Added: {dlg.result['name']}")

    def cmd_edit(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        p = parse_task(self.tasks[idx])
        dlg = TaskDialog(self.root, "Edit Task", initial_data=p)
        if dlg.result:
            self.tasks[idx] = build_task_string(
                p["status"],
                dlg.result["priority"],
                dlg.result["due"],
                dlg.result["name"],
            )
            save_tasks(self.tasks)
            self.refresh_table()
            self._set_status(f"Updated: {dlg.result['name']}")

    def cmd_delete(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        name = parse_task(self.tasks[idx])["name"]
        if messagebox.askyesno("Confirm Delete",
                               f"Permanently delete:\n\n  {name}"):
            self.tasks.pop(idx)
            save_tasks(self.tasks)
            self.refresh_table()
            self._set_status(f"Deleted: {name}")

    def cmd_mark_complete(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        p = parse_task(self.tasks[idx])
        if p["is_complete"]:
            self._set_status(f"Already complete: {p['name']}")
            return
        self.tasks[idx] = build_task_string("[X]", p["priority"],
                                            p["due"], p["name"])
        save_tasks(self.tasks)
        self.refresh_table()
        self._set_status(f"✅  Completed: {p['name']}")

    def cmd_mark_incomplete(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        p = parse_task(self.tasks[idx])
        if not p["is_complete"]:
            self._set_status(f"Already incomplete: {p['name']}")
            return
        self.tasks[idx] = build_task_string("[ ]", p["priority"],
                                            p["due"], p["name"])
        save_tasks(self.tasks)
        self.refresh_table()
        self._set_status(f"Marked incomplete: {p['name']}")

    def cmd_stats(self) -> None:
        if not self.tasks:
            messagebox.showinfo("Statistics", "No tasks yet — add some first!")
            return
        StatsWindow(self.root, self.tasks)

    def cmd_export(self) -> None:
        if not self.tasks:
            messagebox.showinfo("Export", "No tasks to export.")
            return
        filename = export_to_file(self.tasks)
        messagebox.showinfo("Exported",
                            f"Tasks exported to:\n{filename}")
        self._set_status(f"Exported → {filename}")


# ══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def main() -> None:
    root = tk.Tk()
    TaskManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import datetime
import threading
import json
import time
import os

DATA_FILE = "tasks.json"

class Task:
    def __init__(self, title, description, due_date, importance, status="Pending", notified=False):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.importance = importance
        self.status = status
        self.notified = notified

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "importance": self.importance,
            "status": self.status,
            "notified": self.notified
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["title"],
            data["description"],
            data["due_date"],
            data["importance"],
            data.get("status", "Pending"),
            data.get("notified", False)
        )

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📋 Task Manager")
        self.tasks = self.load_tasks()
        self.filtered_tasks = self.tasks

        self.build_ui()
        self.filter_tasks()
        threading.Thread(target=self.reminder_loop, daemon=True).start()

    def build_ui(self):
        tk.Label(self.root, text="Search:").grid(row=0, column=0, sticky="w", padx=5)
        self.search_entry = tk.Entry(self.root, width=40)
        self.search_entry.grid(row=0, column=1, columnspan=3, pady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_tasks)

        tk.Label(self.root, text="Title:").grid(row=1, column=0, sticky="w", padx=5)
        self.title_entry = tk.Entry(self.root, width=40)
        self.title_entry.grid(row=1, column=1, columnspan=3, pady=5)

        tk.Label(self.root, text="Description:").grid(row=2, column=0, sticky="w", padx=5)
        self.desc_entry = tk.Entry(self.root, width=40)
        self.desc_entry.grid(row=2, column=1, columnspan=3, pady=5)

        tk.Label(self.root, text="Due Date:").grid(row=3, column=0, sticky="w", padx=5)
        self.due_date = DateEntry(self.root, date_pattern="yyyy-mm-dd")
        self.due_date.grid(row=3, column=1, pady=5, sticky="w")

        tk.Label(self.root, text="Time (HH:MM):").grid(row=3, column=2, sticky="e")
        self.time_entry = tk.Entry(self.root, width=10)
        self.time_entry.grid(row=3, column=3, pady=5, sticky="w")

        tk.Label(self.root, text="Importance:").grid(row=4, column=0, sticky="w", padx=5)
        self.importance = ttk.Combobox(self.root, values=["High 🔴", "Medium 🟠", "Low 🟡"])
        self.importance.grid(row=4, column=1, pady=5, sticky="w")
        self.importance.set("Medium 🟠")

        tk.Button(self.root, text="➕ Add Task", command=self.add_task).grid(row=4, column=2)
        tk.Button(self.root, text="✔ Done", command=self.mark_done).grid(row=4, column=3)
        tk.Button(self.root, text="🗑 Delete", command=self.delete_task).grid(row=5, column=3)

        self.task_listbox = tk.Listbox(self.root, width=80, height=15)
        self.task_listbox.grid(row=6, column=0, columnspan=4, padx=10, pady=10)
        self.task_listbox.bind("<<ListboxSelect>>", self.color_selected)

    def add_task(self):
        title = self.title_entry.get().strip()
        desc = self.desc_entry.get().strip()
        date = self.due_date.get_date()
        time_str = self.time_entry.get().strip()
        importance = self.importance.get()

        if not title or not time_str:
            messagebox.showwarning("Missing Info", "Title and Time are required.")
            return

        try:
            dt = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Invalid Time", "Use HH:MM format.")
            return

        task = Task(title, desc, dt.strftime("%Y-%m-%d %H:%M"), importance)
        self.tasks.append(task)
        self.clear_inputs()
        self.filter_tasks()

    def mark_done(self):
        sel = self.task_listbox.curselection()
        if sel:
            task = self.filtered_tasks[sel[0]]
            task.status = "Completed"
            self.filter_tasks()

    def delete_task(self):
        sel = self.task_listbox.curselection()
        if sel:
            task = self.filtered_tasks[sel[0]]
            self.tasks.remove(task)
            self.filter_tasks()

    def clear_inputs(self):
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.importance.set("Medium 🟠")

    def filter_tasks(self, event=None):
        q = self.search_entry.get().lower().strip()
        self.filtered_tasks = sorted(
            [t for t in self.tasks if q in t.title.lower() or q in t.description.lower()],
            key=lambda x: x.due_date
        )
        self.task_listbox.delete(0, tk.END)
        for t in self.filtered_tasks:
            label = f"[{t.status}] {t.title} - {t.due_date} ({t.importance})"
            self.task_listbox.insert(tk.END, label)

    def color_selected(self, event=None):
        sel = self.task_listbox.curselection()
        if not sel:
            return
        task = self.filtered_tasks[sel[0]]
        color = "black"
        if "High" in task.importance:
            color = "red"
        elif "Medium" in task.importance:
            color = "orange"
        elif "Low" in task.importance:
            color = "green"
        self.task_listbox.itemconfig(sel[0], {'fg': color})

    def reminder_loop(self):
        while True:
            now = datetime.now()
            for task in self.tasks:
                if task.status == "Pending" and not task.notified:
                    try:
                        due = datetime.strptime(task.due_date, "%Y-%m-%d %H:%M")
                        if 0 < (due - now).total_seconds() <= 60:
                            task.notified = True
                            self.root.after(0, lambda t=task: self.show_reminder(t))
                    except:
                        pass
            time.sleep(10)

    def show_reminder(self, task):
        threading.Thread(target=self.play_alarm, daemon=True).start()
        popup = tk.Toplevel(self.root)
        popup.title("⏰ Reminder")
        tk.Label(popup, text=f"'{task.title}' is due at {task.due_date}").pack(pady=10)
        tk.Button(popup, text="Snooze 5 min", command=lambda: self.snooze(task, popup)).pack(side="left", padx=10)
        tk.Button(popup, text="Dismiss", command=popup.destroy).pack(side="right", padx=10)

    def snooze(self, task, popup):
        popup.destroy()
        task.notified = False
        threading.Timer(300, lambda: self.show_reminder(task)).start()

    def play_alarm(self):
        for _ in range(3):
            os.system("afplay /System/Library/Sounds/Glass.aiff")
            time.sleep(1)

    def load_tasks(self):
        try:
            with open(DATA_FILE, "r") as f:
                return [Task.from_dict(d) for d in json.load(f)]
        except FileNotFoundError:
            return []

    def save_tasks(self):
        with open(DATA_FILE, "w") as f:
            json.dump([t.to_dict() for t in self.tasks], f)

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.save_tasks)
    root.mainloop()

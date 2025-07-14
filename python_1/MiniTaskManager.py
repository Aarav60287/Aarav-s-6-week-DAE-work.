import json
import threading
import time
from datetime import datetime

class Task:
    def __init__(self, title, description, due_date):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.status = "Pending"

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(data['title'], data['description'], data['due_date'])
        task.status = data['status']
        return task

def save_tasks(tasks):
    with open("tasks.json", "w") as f:
        json.dump([task.to_dict() for task in tasks], f)

def load_tasks():
    try:
        with open("tasks.json", "r") as f:
            return [Task.from_dict(data) for data in json.load(f)]
    except FileNotFoundError:
        return []

def add_task(tasks):
    title = input("Enter title: ")
    description = input("Enter description: ")

    while True:
        due_date = input("Enter due date (YYYY-MM-DD HH:MM): ")
        try:
            datetime.strptime(due_date, "%Y-%m-%d %H:%M")
            break
        except ValueError:
            print("❌ Invalid format. Please try again.")

    task = Task(title, description, due_date)
    tasks.append(task)
    print("✅ Task added!")

def list_tasks(tasks):
    if not tasks:
        print("No tasks yet.")
        return
    for i, task in enumerate(tasks):
        print(f"{i + 1}. [{task.status}] {task.title} - Due: {task.due_date}")
        print(f"   Description: {task.description}")

def mark_done(tasks):
    list_tasks(tasks)
    try:
        num = int(input("Enter task number to mark as done: "))
        if 1 <= num <= len(tasks):
            tasks[num - 1].status = "Completed"
            print("✅ Task marked as done.")
        else:
            print("❌ Invalid task number.")
    except ValueError:
        print("❌ Please enter a number.")

def delete_task(tasks):
    list_tasks(tasks)
    try:
        num = int(input("Enter task number to delete: "))
        if 1 <= num <= len(tasks):
            deleted = tasks.pop(num - 1)
            print(f"🗑️ Deleted task: {deleted.title}")
        else:
            print("❌ Invalid task number.")
    except ValueError:
        print("❌ Please enter a number.")

def reminder_loop(tasks):
    while True:
        now = datetime.now()
        for task in tasks:
            if task.status == "Pending":
                try:
                    due = datetime.strptime(task.due_date, "%Y-%m-%d %H:%M")
                    time_left = (due - now).total_seconds()
                    if 0 < time_left <= 600:
                        print(f"\n⏰ Reminder: '{task.title}' is due soon at {task.due_date}!\n")
                except Exception:
                    pass
        time.sleep(30)

def main():
    tasks = load_tasks()

    reminder_thread = threading.Thread(target=reminder_loop, args=(tasks,), daemon=True)
    reminder_thread.start()

    while True:
        print("\n📋 Mini Task Manager")
        print("1. Add Task")
        print("2. List Tasks")
        print("3. Mark Task as Done")
        print("4. Delete Task")
        print("5. Save and Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            list_tasks(tasks)
        elif choice == "3":
            mark_done(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "5":
            save_tasks(tasks)
            print("✅ Tasks saved. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1–5.")

if __name__ == "__main__":
    main()


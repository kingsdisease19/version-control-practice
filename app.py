import os
import datetime

TASKS_FILE = "tasks.txt"

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as file:
        tasks = []
        for line in file.readlines():
            line = line.strip()
            if line:
                tasks.append(line)
        return tasks

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        for task in tasks:
            file.write(task + "\n")

def parse_task(task_str):
    parts = task_str.split("|")
    if len(parts) == 4:
        status = parts[0].strip()
        priority = parts[1].strip()
        due = parts[2].strip()
        name = parts[3].strip()
    else:
        status = "[ ]"
        priority = "Medium"
        due = "No due date"
        name = task_str
    return status, priority, due, name

def format_task(status, priority, due, name):
    return f"{status} | {priority} | {due} | {name}"

def show_tasks(tasks, filter_status=None, filter_priority=None):
    if not tasks:
        print("No tasks found.")
        return

    print("\n" + "=" * 65)
    print(f"{'#':<4} {'STATUS':<6} {'PRIORITY':<10} {'DUE DATE':<15} {'TASK'}")
    print("=" * 65)

    displayed = 0
    for i, task in enumerate(tasks, start=1):
        status, priority, due, name = parse_task(task)

        if filter_status and filter_status not in status:
            continue
        if filter_priority and filter_priority.lower() != priority.lower():
            continue

        status_symbol = "DONE" if "[X]" in status else "    "
        print(f"{i:<4} {status_symbol:<6} {priority:<10} {due:<15} {name}")
        displayed += 1

    print("=" * 65)
    if displayed == 0:
        print("No tasks match your filter.")
    else:
        print(f"Showing {displayed} of {len(tasks)} tasks.")

def add_task(tasks):
    print("\n--- Add New Task ---")
    name = input("Task name: ").strip()
    if not name:
        print("Task name cannot be empty.")
        return

    print("Priority: 1) High  2) Medium  3) Low")
    priority_choice = input("Choose priority (default Medium): ").strip()
    priority_map = {"1": "High", "2": "Medium", "3": "Low"}
    priority = priority_map.get(priority_choice, "Medium")

    due = input("Due date (e.g. 2025-12-31) or press Enter to skip: ").strip()
    if not due:
        due = "No due date"

    new_task = format_task("[ ]", priority, due, name)
    tasks.append(new_task)
    save_tasks(tasks)
    print(f"Task added: {name}")

def mark_task_complete(tasks):
    if not tasks:
        print("No tasks available.")
        return
    show_tasks(tasks)
    choice = input("\nEnter task number to mark complete: ").strip()
    try:
        index = int(choice) - 1
        if index < 0 or index >= len(tasks):
            print("Invalid task number.")
            return
        status, priority, due, name = parse_task(tasks[index])
        if "[X]" in status:
            print("Task is already complete.")
            return
        tasks[index] = format_task("[X]", priority, due, name)
        save_tasks(tasks)
        print(f"Marked complete: {name}")
    except ValueError:
        print("Please enter a valid number.")

def mark_task_incomplete(tasks):
    if not tasks:
        print("No tasks available.")
        return
    show_tasks(tasks)
    choice = input("\nEnter task number to mark incomplete: ").strip()
    try:
        index = int(choice) - 1
        if index < 0 or index >= len(tasks):
            print("Invalid task number.")
            return
        status, priority, due, name = parse_task(tasks[index])
        if "[ ]" in status:
            print("Task is already incomplete.")
            return
        tasks[index] = format_task("[ ]", priority, due, name)
        save_tasks(tasks)
        print(f"Marked incomplete: {name}")
    except ValueError:
        print("Please enter a valid number.")

def delete_task(tasks):
    if not tasks:
        print("No tasks to delete.")
        return
    show_tasks(tasks)
    choice = input("\nEnter task number to delete: ").strip()
    try:
        index = int(choice) - 1
        if index < 0 or index >= len(tasks):
            print("Invalid task number.")
            return
        status, priority, due, name = parse_task(tasks[index])
        confirm = input(f"Are you sure you want to delete '{name}'? (yes/no): ").strip().lower()
        if confirm == "yes":
            tasks.pop(index)
            save_tasks(tasks)
            print(f"Deleted: {name}")
        else:
            print("Delete cancelled.")
    except ValueError:
        print("Please enter a valid number.")

def edit_task(tasks):
    if not tasks:
        print("No tasks to edit.")
        return
    show_tasks(tasks)
    choice = input("\nEnter task number to edit: ").strip()
    try:
        index = int(choice) - 1
        if index < 0 or index >= len(tasks):
            print("Invalid task number.")
            return
        status, priority, due, name = parse_task(tasks[index])
        print(f"\nEditing: {name}")
        print("Press Enter to keep the current value.\n")

        new_name = input(f"New task name [{name}]: ").strip()
        if not new_name:
            new_name = name

        print("Priority: 1) High  2) Medium  3) Low")
        priority_choice = input(f"New priority [{priority}]: ").strip()
        priority_map = {"1": "High", "2": "Medium", "3": "Low"}
        new_priority = priority_map.get(priority_choice, priority)

        new_due = input(f"New due date [{due}]: ").strip()
        if not new_due:
            new_due = due

        tasks[index] = format_task(status, new_priority, new_due, new_name)
        save_tasks(tasks)
        print("Task updated successfully.")
    except ValueError:
        print("Please enter a valid number.")

def search_tasks(tasks):
    if not tasks:
        print("No tasks to search.")
        return
    keyword = input("Enter keyword to search: ").strip().lower()
    if not keyword:
        print("No keyword entered.")
        return

    print("\n--- Search Results ---")
    found = 0
    for i, task in enumerate(tasks, start=1):
        status, priority, due, name = parse_task(task)
        if keyword in name.lower():
            status_label = "DONE" if "[X]" in status else "    "
            print(f"{i}. [{status_label}] [{priority}] [{due}] {name}")
            found += 1

    if found == 0:
        print(f"No tasks found matching '{keyword}'.")
    else:
        print(f"\n{found} task(s) found.")

def show_statistics(tasks):
    if not tasks:
        print("No tasks available.")
        return

    total = len(tasks)
    completed = sum(1 for t in tasks if "[X]" in t)
    incomplete = total - completed
    high = sum(1 for t in tasks if "| High |" in t)
    medium = sum(1 for t in tasks if "| Medium |" in t)
    low = sum(1 for t in tasks if "| Low |" in t)
    percent = (completed / total * 100) if total > 0 else 0
    bar_filled = int(percent / 5)
    progress_bar = "[" + "#" * bar_filled + "-" * (20 - bar_filled) + "]"

    print("\n--- Task Statistics ---")
    print(f"Total tasks    : {total}")
    print(f"Completed      : {completed}")
    print(f"Incomplete     : {incomplete}")
    print(f"Progress       : {progress_bar} {percent:.1f}%")
    print(f"\nHigh Priority  : {high}")
    print(f"Medium Priority: {medium}")
    print(f"Low Priority   : {low}")

def filter_tasks(tasks):
    print("\n--- Filter Tasks ---")
    print("1. Show only completed tasks")
    print("2. Show only incomplete tasks")
    print("3. Filter by priority")
    choice = input("Choose filter: ").strip()

    if choice == "1":
        show_tasks(tasks, filter_status="[X]")
    elif choice == "2":
        show_tasks(tasks, filter_status="[ ]")
    elif choice == "3":
        print("Priority: 1) High  2) Medium  3) Low")
        p = input("Choose priority: ").strip()
        priority_map = {"1": "High", "2": "Medium", "3": "Low"}
        priority = priority_map.get(p)
        if priority:
            show_tasks(tasks, filter_priority=priority)
        else:
            print("Invalid priority choice.")
    else:
        print("Invalid filter choice.")

def sort_tasks(tasks):
    if not tasks:
        print("No tasks to sort.")
        return

    print("\n--- Sort Tasks ---")
    print("1. Sort by priority (High first)")
    print("2. Sort by status (Incomplete first)")
    print("3. Sort by name (A to Z)")
    choice = input("Choose sort option: ").strip()

    priority_order = {"High": 0, "Medium": 1, "Low": 2}

    if choice == "1":
        tasks.sort(key=lambda t: priority_order.get(parse_task(t)[1], 3))
        print("Sorted by priority.")
    elif choice == "2":
        tasks.sort(key=lambda t: 0 if "[ ]" in parse_task(t)[0] else 1)
        print("Sorted by status.")
    elif choice == "3":
        tasks.sort(key=lambda t: parse_task(t)[3].lower())
        print("Sorted alphabetically.")
    else:
        print("Invalid sort option.")
        return

    save_tasks(tasks)
    show_tasks(tasks)

def clear_completed(tasks):
    completed = [t for t in tasks if "[X]" in t]
    if not completed:
        print("No completed tasks to clear.")
        return
    confirm = input(f"Delete all {len(completed)} completed task(s)? (yes/no): ").strip().lower()
    if confirm == "yes":
        tasks[:] = [t for t in tasks if "[X]" not in t]
        save_tasks(tasks)
        print(f"Cleared {len(completed)} completed task(s).")
    else:
        print("Cancelled.")

def export_tasks(tasks):
    if not tasks:
        print("No tasks to export.")
        return
    filename = f"tasks_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w") as f:
        f.write("TASK EXPORT\n")
        f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 65 + "\n")
        f.write(f"{'#':<4} {'STATUS':<6} {'PRIORITY':<10} {'DUE DATE':<15} {'TASK'}\n")
        f.write("=" * 65 + "\n")
        for i, task in enumerate(tasks, start=1):
            status, priority, due, name = parse_task(task)
            status_label = "DONE" if "[X]" in status else "    "
            f.write(f"{i:<4} {status_label:<6} {priority:<10} {due:<15} {name}\n")
        f.write("=" * 65 + "\n")
        f.write(f"Total: {len(tasks)} tasks\n")
    print(f"Tasks exported to: {filename}")

def main():
    tasks = load_tasks()

    while True:
        print("\n" + "=" * 35)
        print("       CLI TASK MANAGER")
        print("=" * 35)
        print(" 1.  View All Tasks")
        print(" 2.  Add Task")
        print(" 3.  Mark Task Complete")
        print(" 4.  Mark Task Incomplete")
        print(" 5.  Edit Task")
        print(" 6.  Delete Task")
        print(" 7.  Search Tasks")
        print(" 8.  Filter Tasks")
        print(" 9.  Sort Tasks")
        print("10.  Statistics")
        print("11.  Clear Completed Tasks")
        print("12.  Export Tasks to File")
        print("13.  Exit")
        print("=" * 35)

        choice = input("Choose an option: ").strip()

        if choice == "1":
            show_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            mark_task_complete(tasks)
        elif choice == "4":
            mark_task_incomplete(tasks)
        elif choice == "5":
            edit_task(tasks)
        elif choice == "6":
            delete_task(tasks)
        elif choice == "7":
            search_tasks(tasks)
        elif choice == "8":
            filter_tasks(tasks)
        elif choice == "9":
            sort_tasks(tasks)
        elif choice == "10":
            show_statistics(tasks)
        elif choice == "11":
            clear_completed(tasks)
        elif choice == "12":
            export_tasks(tasks)
        elif choice == "13":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose 1 to 13.")

if __name__ == "__main__":
    main()
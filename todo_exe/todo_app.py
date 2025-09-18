import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import json
import os
from datetime import datetime

TASK_FILE = "tasks.json"

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced To-Do List")
        self.root.geometry("600x600")
        self.tasks = []
        
        # Entry for new tasks
        self.entry_frame = tk.Frame(root)
        self.entry_frame.pack(pady=10)
        
        self.task_entry = tk.Entry(self.entry_frame, width=30)
        self.task_entry.pack(side=tk.LEFT, padx=5)
        self.task_entry.bind('<Return>', lambda event: self.add_task())
        
        self.priority_var = tk.StringVar(value="Medium")
        self.priority_menu = ttk.Combobox(self.entry_frame, textvariable=self.priority_var, values=["High", "Medium", "Low"], width=8)
        self.priority_menu.pack(side=tk.LEFT, padx=5)
        
        self.due_entry = tk.Entry(self.entry_frame, width=12)
        self.due_entry.pack(side=tk.LEFT, padx=5)
        self.due_entry.insert(0, "YYYY-MM-DD")
        
        self.add_button = tk.Button(self.entry_frame, text="Add Task", command=self.add_task)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        # Search bar
        self.search_frame = tk.Frame(root)
        self.search_frame.pack(pady=5)
        self.search_entry = tk.Entry(self.search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda event: self.update_listbox())
        tk.Label(self.search_frame, text="Filter:").pack(side=tk.LEFT)
        
        # Scrollable listbox
        self.list_frame = tk.Frame(root)
        self.list_frame.pack(pady=10)
        
        self.scrollbar = tk.Scrollbar(self.list_frame, orient=tk.VERTICAL)
        self.task_listbox = tk.Listbox(
            self.list_frame, width=70, height=20, yscrollcommand=self.scrollbar.set
        )
        self.scrollbar.config(command=self.task_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        
        # Buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)
        
        tk.Button(self.button_frame, text="Edit Task", command=self.edit_task).grid(row=0, column=0, padx=5)
        tk.Button(self.button_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=1, padx=5)
        tk.Button(self.button_frame, text="Mark Complete", command=self.complete_task).grid(row=0, column=2, padx=5)
        tk.Button(self.button_frame, text="Clear All", command=self.clear_tasks).grid(row=0, column=3, padx=5)
        tk.Button(self.button_frame, text="Save Tasks", command=self.save_tasks).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(self.button_frame, text="Load Tasks", command=self.load_tasks).grid(row=1, column=1, padx=5, pady=5)
        
        self.load_tasks()
        self.check_due_today()
        
    def add_task(self):
        task_name = self.task_entry.get().strip()
        priority = self.priority_var.get()
        due_date = self.due_entry.get().strip()
        
        if task_name:
            # Validate due date
            if due_date != "YYYY-MM-DD" and due_date != "":
                try:
                    datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Due date must be in YYYY-MM-DD format")
                    return
            else:
                due_date = ""
                
            self.tasks.append({
                "task": task_name,
                "priority": priority,
                "due": due_date,
                "completed": False
            })
            self.update_listbox()
            self.task_entry.delete(0, tk.END)
            self.due_entry.delete(0, tk.END)
            self.due_entry.insert(0, "YYYY-MM-DD")
        else:
            messagebox.showwarning("Warning", "Task cannot be empty!")
    
    def edit_task(self):
        selected = self.task_listbox.curselection()
        if selected:
            index = selected[0]
            current_task = self.tasks[index]
            
            new_task_name = simpledialog.askstring("Edit Task", "Edit your task:", initialvalue=current_task["task"])
            if new_task_name:
                new_priority = simpledialog.askstring("Edit Priority", "Priority (High/Medium/Low):", initialvalue=current_task["priority"])
                new_due = simpledialog.askstring("Edit Due Date", "Due date YYYY-MM-DD (optional):", initialvalue=current_task["due"])
                if new_due:
                    try:
                        datetime.strptime(new_due, "%Y-%m-%d")
                    except ValueError:
                        messagebox.showerror("Error", "Due date must be in YYYY-MM-DD format")
                        return
                self.tasks[index]["task"] = new_task_name
                self.tasks[index]["priority"] = new_priority if new_priority in ["High","Medium","Low"] else "Medium"
                self.tasks[index]["due"] = new_due
                self.update_listbox()
        else:
            messagebox.showwarning("Warning", "Select a task to edit")
    
    def delete_task(self):
        selected = self.task_listbox.curselection()
        if selected:
            index = selected[0]
            del self.tasks[index]
            self.update_listbox()
        else:
            messagebox.showwarning("Warning", "Select a task to delete")
    
    def complete_task(self):
        selected = self.task_listbox.curselection()
        if selected:
            index = selected[0]
            self.tasks[index]["completed"] = not self.tasks[index]["completed"]
            self.update_listbox()
        else:
            messagebox.showwarning("Warning", "Select a task to mark complete")
    
    def clear_tasks(self):
        if messagebox.askyesno("Clear All", "Are you sure you want to delete all tasks?"):
            self.tasks.clear()
            self.update_listbox()
    
    def save_tasks(self):
        with open(TASK_FILE, "w") as f:
            json.dump(self.tasks, f)
        messagebox.showinfo("Saved", "Tasks saved successfully!")
    
    def load_tasks(self):
        if os.path.exists(TASK_FILE):
            with open(TASK_FILE, "r") as f:
                self.tasks = json.load(f)
        self.update_listbox()
    
    def update_listbox(self):
        self.task_listbox.delete(0, tk.END)
        filter_text = self.search_entry.get().lower()
        for task in self.tasks:
            display_text = f"{task['task']} [Priority: {task['priority']}]"
            if task["due"]:
                display_text += f" [Due: {task['due']}]"
            if task["completed"]:
                display_text += " ✅"
            # Filtering
            if filter_text in task['task'].lower() or filter_text in task['priority'].lower():
                self.task_listbox.insert(tk.END, display_text)
    
    def check_due_today(self):
        today = datetime.today().strftime("%Y-%m-%d")
        for task in self.tasks:
            if task["due"] == today and not task["completed"]:
                messagebox.showinfo("Reminder", f"Task due today: {task['task']}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()

import tkinter as tk
from tkinter import ttk

# Global variable to store the last selected value
last_selected_value = None

def update_last_selected_value(event=None):
    """Callback function to update the last selected value."""
    global last_selected_value
    last_selected_value = combo.get()

def on_combobox_change(event):
    """Callback function to check if the value has changed."""
    global last_selected_value
    current_value = combo.get()
    if current_value!= last_selected_value:
        print(f"Value changed to {current_value}")
        # Update the last selected value
        last_selected_value = current_value
    else:
        print(f"Same value selected: {current_value}")

root = tk.Tk()
combo = ttk.Combobox(root, values=["Option 1", "Option 2", "Option 3"])
combo.pack()

# Bind the <<ComboboxSelected>> event to the on_combobox_change function
combo.bind("<<ComboboxSelected>>", on_combobox_change)

# Initially populate the last_selected_value
update_last_selected_value()

root.mainloop()

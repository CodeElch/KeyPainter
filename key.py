import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import json

DEFAULT_COLOR = 'white'

# Vollständige QWERTZ-Tastaturbelegung
keyboard_rows = [
    ['esc', 'F1', 'F2', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'Druck', 'Rollen', 'Pause'],
    ['^', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'ß', '´', '<--', 'einf', 'Pos1', 'BildUp', 'NumLock', 'NUM/', 'NUM*', 'NUM-'],
    ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Z', 'U', 'I', 'O', 'P', 'Ü', '+', 'Enter', 'Entf', 'Ende', 'BildDown', 'NUM7', 'NUM8', 'NUM9', 'NUM+'],
    ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ö', 'Ä', '#', 'Enter', '', '', '', 'NUM4', 'NUM5', 'NUM6'],
    ['LShift', 'Y', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '-', 'rShift', 'Up', 'NUM1', 'NUM2', 'NUM3', 'NUM,', 'Num0'],
    ['LStrg', 'Win', 'Alt', 'Space', 'AltGr', 'FN', 'List', 'Strg', 'Links', 'Unten', 'Rechts', 'NUM0', 'NUM,']
]

class KeyInfo:
    def __init__(self, labels, color=DEFAULT_COLOR):
        self.labels = labels
        self.color = color

# Initialisiere Tastenbelegungen
keys = {}
for row in keyboard_rows:
    for key in row:
        keys[key] = KeyInfo([key], DEFAULT_COLOR)

def compute_button_width(key):
    """
    Berechnet eine angemessene Breite für den Button.
    Als Basis dient die Länge des längsten Strings (Standardkey und zusätzliche Beschriftungen),
    wobei ein Puffer von 2 Zeichen hinzugefügt wird. Es wird mindestens eine Breite von 6 Zeichen verwendet.
    """
    texts = keys[key].labels + [key]
    max_length = max(len(text) for text in texts)
    return max(6, max_length + 2)

undo_stack = []
redo_stack = []

def save_state():
    """
    Save the current state of the keys for undo functionality.
    """
    undo_stack.append(json.dumps({k: {'labels': v.labels, 'color': v.color} for k, v in keys.items()}))
    if len(undo_stack) > 10:  # Limit the stack size
        undo_stack.pop(0)

def undo(buttons, listbox):
    """
    Undo the last change.
    """
    if undo_stack:
        redo_stack.append(json.dumps({k: {'labels': v.labels, 'color': v.color} for k, v in keys.items()}))
        state = json.loads(undo_stack.pop())
        for key in keys:
            keys[key].labels = state[key]['labels']
            keys[key].color = state[key]['color']
            buttons[key].config(bg=state[key]['color'], text=key, width=compute_button_width(key))
        update_listbox(listbox, keys)

def redo(buttons, listbox):
    """
    Redo the last undone change.
    """
    if redo_stack:
        save_state()
        state = json.loads(redo_stack.pop())
        for key in keys:
            keys[key].labels = state[key]['labels']
            keys[key].color = state[key]['color']
            buttons[key].config(bg=state[key]['color'], text=key, width=compute_button_width(key))
        update_listbox(listbox, keys)

def main():
    """
    Main function to initialize and run the Tkinter application.
    """
    root = tk.Tk()
    root.title("KeyPainter")
    
    # Container-Frames
    keyboard_frame = ttk.Frame(root, padding=10)
    keyboard_frame.pack()
    
    list_frame = ttk.Frame(root)
    list_frame.pack(padx=10, pady=10, fill='both')
    
    # Listbox with Scrollbar
    listbox = tk.Listbox(list_frame, width=40)
    scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=listbox.yview)
    listbox.config(yscrollcommand=scrollbar.set)
    
    update_listbox(listbox, keys)  # Initial filling of the listbox
    
    scrollbar.pack(side='right', fill='y')
    listbox.pack(side='left', fill='both', expand=True)
    
    # Create keyboard buttons using grid layout
    buttons = {}
    for row_index, row in enumerate(keyboard_rows):
        for col_index, key in enumerate(row):
            btn = tk.Button(
                keyboard_frame, 
                text=key,  # Only show the key name
                width=compute_button_width(key),  # Dynamic width based on label
                bg=keys[key].color,
                command=lambda k=key: change_color(k, buttons, keys, listbox)
            )
            btn.grid(row=row_index, column=col_index, padx=2, pady=2)
            buttons[key] = btn

    # Add search bar
    search_var = tk.StringVar()
    search_var.trace("w", lambda name, index, mode: update_listbox(listbox, keys, search_var.get()))
    search_entry = ttk.Entry(list_frame, textvariable=search_var, width=40)
    search_entry.pack(pady=(0, 5))
    search_entry.insert(0, "")  # Optional placeholder text

    # Menu bar
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(
        label="Speichern", 
        command=lambda: save_config(keys)
    )
    file_menu.add_command(
        label="Laden", 
        command=lambda: load_config(keys, buttons, listbox)
    )
    file_menu.add_command(
        label="Zurücksetzen", 
        command=lambda: reset_config(keys, buttons, listbox)
    )
    menu_bar.add_cascade(label="Datei", menu=file_menu)
    
    edit_menu = tk.Menu(menu_bar, tearoff=0)
    edit_menu.add_command(
        label="Rückgängig", 
        command=lambda: undo(buttons, listbox)
    )
    edit_menu.add_command(
        label="Wiederholen", 
        command=lambda: redo(buttons, listbox)
    )
    menu_bar.add_cascade(label="Bearbeiten", menu=edit_menu)
    
    # Listbox-Ereignisbindung
    listbox.bind('<<ListboxSelect>>', 
        lambda e: show_details(e, keys, listbox, buttons))
    
    root.mainloop()

def change_color(key, buttons, keys, listbox):
    """
    Change the color of a key button and update the listbox.
    """
    save_state()
    color = colorchooser.askcolor()[1]
    if color:
        keys[key].color = color
        buttons[key].config(bg=color)
        update_listbox(listbox, keys)

def show_details(event, keys, listbox, buttons):
    """
    Show a detail window to edit key labels and color.
    """
    selection = listbox.curselection()
    if not selection:
        return
    index = selection[0]
    key = listbox.get(index).split(':')[0].strip()
    
    detail_win = tk.Toplevel()
    detail_win.title(f"Bearbeiten: {key}")
    
    # Labels bearbeiten
    ttk.Label(detail_win, text="Bezeichnungen (kommagetrennt):").pack(pady=5)
    labels_entry = ttk.Entry(detail_win, width=30)
    labels_entry.insert(0, ', '.join(keys[key].labels))
    labels_entry.pack(padx=10)
    
    # Farbe ändern
    color_btn = ttk.Button(
        detail_win,
        text="Farbe wählen",
        command=lambda: change_color(key, buttons, keys, listbox)
    )
    color_btn.pack(pady=5)
    
    # Speichern-Button
    def save_changes():
        save_state()
        new_labels = [l.strip() for l in labels_entry.get().split(',')]
        keys[key].labels = new_labels
        # Aktualisiere den Button: Text und neue Breite anhand der veränderten Beschriftung
        buttons[key].config(text=key, width=compute_button_width(key))  # Only show the key name
        update_listbox(listbox, keys)
        detail_win.destroy()
    
    ttk.Button(detail_win, text="Speichern", command=save_changes).pack(pady=5)

def update_listbox(listbox, keys, search_term=""):
    """
    Update the listbox with keys that match the search term.
    """
    listbox.delete(0, 'end')
    for key in sorted(keys.keys()):  # Remove the duplicate call to update_listbox
        entry = f"{key}: {', '.join(keys[key].labels)}"
        if search_term.lower() in entry.lower():
            listbox.insert('end', entry)

def save_config(keys):
    """
    Save the current key configuration to a JSON file.
    """
    config = {k: {'labels': v.labels, 'color': v.color} for k, v in keys.items()}
    try:
        with open('keyboard_config.json', 'w') as f:
            json.dump(config, f)
        messagebox.showinfo("Erfolg", "Konfiguration gespeichert!")
    except IOError as e:
        messagebox.showerror("Fehler", f"Fehler beim Speichern der Konfiguration: {e}")

def load_config(keys, buttons, listbox):
    """
    Load the key configuration from a JSON file.
    """
    try:
        with open('keyboard_config.json', 'r') as f:
            config = json.load(f)
            for key in keys:
                if key in config:
                    keys[key].labels = config[key]['labels']
                    keys[key].color = config[key]['color']
                    buttons[key].config(
                        bg=config[key]['color'], 
                        text=key,
                        width=compute_button_width(key)
                    )
            update_listbox(listbox, keys)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        messagebox.showerror("Fehler", f"Fehler beim Laden der Konfiguration: {e}")

def reset_config(keys, buttons, listbox):
    """
    Reset the key configuration to the default state.
    """
    for key in keys:
        keys[key].labels = [key]
        keys[key].color = DEFAULT_COLOR
        buttons[key].config(bg=DEFAULT_COLOR, text=key, width=compute_button_width(key))
    update_listbox(listbox, keys)

# Remove the export_to_image function and its call

# Remove the duplicate call to main
if __name__ == "__main__":
    main()

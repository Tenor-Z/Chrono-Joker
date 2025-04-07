"""
-------------------------------------------------------------
  ____  _ ___  __  __  _  __    __   __  _  _____ ___  
 / _/ || | _ \/__\|  \| |/__\  |_ \ /__\| |/ / __| _ \ 
| \_| >< | v / \/ | | ' | \/ |  _\ | \/ |   <| _|| v / 
 \__/_||_|_|_}\__/|_|\__|\__/  /___|\__/|_|\_\___|_|_\ 
-------------------------------------------------------------
                      Written by Tenor-Z
                       April 5, 2025
-------------------------------------------------------------
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import Tk, Label, PhotoImage, Frame
import zlib
import re
from PIL import Image, ImageTk
import random
import os

"""
Balatro uses the 'deflate' algorithm to compress save files to be used in game.
This is a lossless algorithm that combines both LZ77 and Huffman coding. Using
zlib, we can easily decompress the provided save file, which should result into
a readable json format that we can edit using the application
"""

def decompress_deflate(file_data):
    decompressed_data = zlib.decompress(file_data, wbits=-zlib.MAX_WBITS)       #zlib.MAX_WBITS is needed to properly format the save
    return decompressed_data.decode('utf-8')

"""
To compress the save file once more. We can use zlib with level 1 encoding to
return the save into its original format. Any changes or modifications to this
section can result in broken save files or inoperable in-game runs.
"""

def compress_deflate(data):
    compressed_data = zlib.compress(data.encode('utf-8'), level=1)[2:-4]  
    return compressed_data


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)


    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        # Create a toplevel window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip, text=self.text, justify='left',
                         background="#ffffff", relief="solid", borderwidth=1,
                         font=("Arial", "10", "normal"), padx=5, pady=2)
        label.pack(ipadx=1)


    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

"""
This is where the actual window is created
"""

class SaveFileEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Chrono Joker - Balatro Save Editor")
        self.root.geometry("1000x700")
        
        # Try to set icon if it exists
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Set theme colors
        self.bg_color = "#f0f0f0"
        self.accent_color = "#4a6ea9"
        self.button_color = "#5a7ab9"
        self.button_text_color = "white"
        self.text_bg_color = "white"
        self.highlight_color = "#ffeb3b"
        
        self.root.configure(bg=self.bg_color)
        
        # Variables
        self.current_file = None
        self.imported_data = None
        
        # Create a style for ttk widgets
        self.style = ttk.Style()
        self.style.configure("TButton", 
                             font=("Arial", 10, "bold"),
                             background=self.button_color,
                             foreground=self.button_text_color)
        self.style.configure("TLabel", 
                             font=("Arial", 10),
                             background=self.bg_color)
        self.style.configure("TFrame", 
                             background=self.bg_color)
        self.style.configure("Header.TLabel", 
                             font=("Arial", 16, "bold"),
                             background=self.bg_color)
        self.style.configure("Status.TLabel", 
                             font=("Arial", 9),
                             background=self.bg_color)
        self.style.configure("Slogan.TLabel", 
                             font=("Comic Sans MS", 10),
                             foreground="red",
                             background=self.bg_color)
        
        self.main_container = ttk.Frame(self.root, style="TFrame")
        self.main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.create_header()
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill="both", expand=True, pady=10)
        
        # Create tabs
        self.editor_tab = ttk.Frame(self.notebook, style="TFrame")
        self.raw_data_tab = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.editor_tab, text="Editor")
        self.notebook.add(self.raw_data_tab, text="Raw Data")
        
        self.create_editor_tab()
        
        self.create_raw_data_tab()
        
        # Create status bar
        self.create_status_bar()
        
        self.slogans = [
            "We all know why you're here!",
            "I guess we all know who the real Joker is around here!",
            "Cheaters never win, you know?",
            "If you can't beat 'em... cheat 'em.",
            "You're making me feel a bit flushed here",
            "The house always wins... unless you edit the save",
            "Luck is for chumps. We prefer guarantees!",
            "Stacking the deck? More like rewriting it.",
            "Jokers? How about gods?",
            "Call it an exploit. I call it a strategy.",
            "Ante up? Nah, max it out.",
            "Fair play? Never heard of it.",
            "Bluffing is for amateurs.",
            "From bust to billionaire in just one click.",
            "Would you like some loaded dice with that?",
            "Just one more tweak... and another... and another...",
            "Remember: If you get caught, I was never here.",
            "I bet the devs didn't see this coming.",
            "Consider this a 'strategic rebalancing'",
            "Winning with skill? How about winning with science?",
            "Odds? We don't do those over here...",
            "The dealer is shaking in his boots."
        ]
        
        # Start slogan rotation
        self.update_slogan()
    
    """
    When the user clicks on the About button
    """

    def show_about_dialog(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About Chrono Joker")
        about_window.geometry("400x800")
        about_window.configure(bg=self.bg_color)
        about_window.resizable(False, False)
    
    # Center the window
        about_window.transient(self.root)
        about_window.grab_set()
    
    # Try to set icon. If not, oh well
        try:
            about_window.iconbitmap("icon.ico")
        except:
            pass
    
        container = ttk.Frame(about_window, style="TFrame")
        container.pack(fill="both", expand=True, padx=20, pady=20)
    
        try:
            img = Image.open("logo.png")
            img = img.resize((150, 200))  # Larger size for about page
            photo = ImageTk.PhotoImage(img)
            logo_label = Label(container, image=photo, bg=self.bg_color)
            logo_label.image = photo  # Keep reference
            logo_label.pack(pady=(0, 20))
        except:

        # If logo not found, just show the title

            title_label = ttk.Label(container, text="Chrono Joker", 
                               font=("Arial", 24, "bold"),
                               style="Header.TLabel")
            title_label.pack(pady=(0, 20))
    
    # App name and version
        app_name = ttk.Label(container, text="Balatro Save Editor", 
                        font=("Arial", 16, "bold"),
                        style="Header.TLabel")
        app_name.pack()
    
        version = ttk.Label(container, text="Version 2.0", style="TLabel")
        version.pack(pady=(0, 20))
    
    # Description
        description = """Chrono Joker is a save file editor for Balatro that allows you to modify game parameters such as money, ante, 
        joker limits, and more.
    
Use at your own risk - modifying save files may impact your game experience."""
    
        desc_label = ttk.Label(container, text=description, 
                          justify="center", wraplength=350,
                          style="TLabel")
        desc_label.pack(pady=10)
    
    # Credits
        credits_frame = ttk.LabelFrame(container, text="                                         Credits", style="TFrame")
        credits_frame.pack(fill="x", pady=20, padx=20)
    
        credits_text = ttk.Label(credits_frame, 
                            text="Developed by: Tyler Bifolchi (Tenor-Z)\nContact: tjbifolchi@outlook.com", 
                            justify="center",
                            style="TLabel")
        credits_text.pack(pady=10)
    
    # Close button
        close_button = tk.Button(container, text="Close", 
                            command=about_window.destroy,
                            bg=self.button_color, fg=self.button_text_color,
                            font=("Arial", 10, "bold"), padx=20, pady=5,
                            relief="flat", borderwidth=0)
        close_button.pack(pady=20)
    
    # Copyright
        copyright_label = ttk.Label(container, 
                               text="© 2025 All Rights Reserved", 
                               style="Status.TLabel")
        copyright_label.pack(side="bottom", pady=10)


    def create_header(self):
        header_frame = ttk.Frame(self.main_container, style="TFrame")
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Try to load logo image
        try:
            img = Image.open("logo.png")
            img = img.resize((100, 150))  # Smaller size for header
            photo = ImageTk.PhotoImage(img)
            logo_label = Label(header_frame, image=photo, bg=self.bg_color)
            logo_label.image = photo  # Keep reference
            logo_label.pack(side="left", padx=(0, 10))
        except:
            pass  # Skip if image not found

        title_frame = ttk.Frame(header_frame, style="TFrame")
        title_frame.pack(side="left", fill="y")
        
        title_label = ttk.Label(title_frame, text="Chrono Joker", style="Header.TLabel")
        title_label.pack(anchor="w")
        
        subtitle_label = ttk.Label(title_frame, text="Edit your Balatro save files!", style="TLabel")
        subtitle_label.pack(anchor="w")
        
        self.slogan_label = ttk.Label(header_frame, text="", style="Slogan.TLabel")
        self.slogan_label.pack(side="right", padx=10)
    

    def create_editor_tab(self):
        button_frame = ttk.Frame(self.editor_tab, style="TFrame")
        button_frame.pack(fill="x", pady=10)
        
        # Create styled buttons
        import_button = tk.Button(button_frame, text="Import Save File", 
                                 command=self.import_save_file,
                                 bg=self.button_color, fg=self.button_text_color,
                                 font=("Arial", 10, "bold"), padx=10, pady=5,
                                 relief="flat", borderwidth=0)
        import_button.grid(row=0, column=0, padx=5)
        ToolTip(import_button, "Import a .jkr save file")       # the import save button
        
        export_button = tk.Button(button_frame, text="Export Save File", 
                                 command=self.export_save_file,
                                 bg=self.button_color, fg=self.button_text_color,
                                 font=("Arial", 10, "bold"), padx=10, pady=5,
                                 relief="flat", borderwidth=0)
        export_button.grid(row=0, column=1, padx=5)
        ToolTip(export_button, "Export modified save file")         # The export save button
        
        editor_button = tk.Button(button_frame, text="Edit Saved Run", 
                                 command=self.open_save_editor,
                                 bg=self.button_color, fg=self.button_text_color,
                                 font=("Arial", 10, "bold"), padx=10, pady=5,
                                 relief="flat", borderwidth=0)
        editor_button.grid(row=0, column=2, padx=5)
        ToolTip(editor_button, "Edit the parameters of the saved run")              # The Edit Saved Run button
        
        find_button = tk.Button(button_frame, text="Find", 
                               command=self.find_text,
                               bg=self.button_color, fg=self.button_text_color,
                               font=("Arial", 10, "bold"), padx=10, pady=5,
                               relief="flat", borderwidth=0)
        find_button.grid(row=0, column=3, padx=5)
        ToolTip(find_button, "Search for text in the save file")                # The Find button

        about_button = tk.Button(button_frame, text="About", 
                            command=self.show_about_dialog,
                            bg=self.button_color, fg=self.button_text_color,
                            font=("Arial", 10, "bold"), padx=10, pady=5,
                            relief="flat", borderwidth=0)
        about_button.grid(row=0, column=4, padx=5)
        ToolTip(about_button, "About this application")                         # The About button         
        
        # Quick actions frame
        quick_frame = ttk.LabelFrame(self.editor_tab, text="Quick Actions", style="TFrame")
        quick_frame.pack(fill="x", pady=10, padx=5)
        

        # Quick edit buttons
        edit_ante_button = tk.Button(quick_frame, text="Edit Ante", 
                                    command=self.edit_ante,
                                    bg=self.accent_color, fg=self.button_text_color,
                                    font=("Arial", 9), padx=10, pady=3,
                                    relief="flat", borderwidth=0)
        edit_ante_button.pack(side="left", padx=5, pady=5)
        
        edit_money_button = tk.Button(quick_frame, text="Edit Money", 
                                     command=lambda: self.quick_edit_variable("dollars", "Money"),
                                     bg=self.accent_color, fg=self.button_text_color,
                                     font=("Arial", 9), padx=10, pady=3,
                                     relief="flat", borderwidth=0)
        edit_money_button.pack(side="left", padx=5, pady=5)
        
        edit_jokers_button = tk.Button(quick_frame, text="Edit Joker Limit", 
                                      command=lambda: self.quick_edit_variable("max_jokers", "Joker Limit"),
                                      bg=self.accent_color, fg=self.button_text_color,
                                      font=("Arial", 9), padx=10, pady=3,
                                      relief="flat", borderwidth=0)
        edit_jokers_button.pack(side="left", padx=5, pady=5)
        
        # Info frame
        info_frame = ttk.LabelFrame(self.editor_tab, text="File Information", style="TFrame")
        info_frame.pack(fill="x", pady=10, padx=5)
        
        # File info
        self.file_info_label = ttk.Label(info_frame, text="No file loaded", style="TLabel")
        self.file_info_label.pack(anchor="w", padx=10, pady=5)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(self.editor_tab, text="Save Preview", style="TFrame")
        preview_frame.pack(fill="both", expand=True, pady=10, padx=5)
        
        # Preview text area
        self.preview_text = tk.Text(preview_frame, height=10, wrap="none", 
                                   bg=self.text_bg_color, relief="flat",
                                   font=("Consolas", 9))
        self.preview_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.preview_text.config(state="disabled")
    
    def create_raw_data_tab(self):
        # Text frame
        text_frame = ttk.Frame(self.raw_data_tab, style="TFrame")
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Vertical scrollbar
        v_scroll = ttk.Scrollbar(text_frame, orient="vertical")
        v_scroll.pack(side="right", fill="y")
        
        # Horizontal scrollbar
        h_scroll = ttk.Scrollbar(text_frame, orient="horizontal")
        h_scroll.pack(side="bottom", fill="x")
        
        # Text area
        self.text_area = tk.Text(
            text_frame,
            wrap="none",
            bg=self.text_bg_color,
            font=("Consolas", 10),
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )
        self.text_area.pack(side="left", fill="both", expand=True)
        
        # Configure scrollbars
        v_scroll.config(command=self.text_area.yview)
        h_scroll.config(command=self.text_area.xview)

    def create_status_bar(self):
        status_frame = ttk.Frame(self.main_container, style="TFrame")
        status_frame.pack(fill="x", side="bottom", pady=(5, 0))
        
        # Status label
        self.status_label = ttk.Label(status_frame, text="Ready", style="Status.TLabel")
        self.status_label.pack(side="left")
        
        # Version label
        version_label = ttk.Label(status_frame, text="v2.0", style="Status.TLabel")
        version_label.pack(side="right")
    

    def update_slogan(self):
        """Change the slogan to a random one."""
        self.slogan_label.config(text=random.choice(self.slogans))
        # Schedule next update in 5 seconds
        self.root.after(5000, self.update_slogan)
    

    def import_save_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Save Files", "*.jkr")])     # Only .jkr files are supported
        if not file_path:
            return
        
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            decompressed_data = decompress_deflate(file_data)
            
            if decompressed_data:
                # Display the data in the text area
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, decompressed_data)
                
                # Update preview
                self.preview_text.config(state="normal")
                self.preview_text.delete(1.0, tk.END)
                preview_content = decompressed_data[:500] + "..." if len(decompressed_data) > 500 else decompressed_data
                self.preview_text.insert(tk.END, preview_content)
                self.preview_text.config(state="disabled")
                
                # Update file info
                filename = os.path.basename(file_path)
                self.file_info_label.config(text=f"File: {filename}\nPath: {file_path}")
                
                # Store file path and data
                self.current_file = file_path
                self.imported_data = decompressed_data
                
                # Update status
                self.status_label.config(text=f"Loaded file: {filename}")
            else:
                messagebox.showerror("Error", "Failed to decompress save file.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load save file: {e}")
    
    """
    Here when exporting the save file
    """

    def export_save_file(self):
        if not self.current_file:
            messagebox.showerror("Error", "No file loaded to save.")
            return
        
        # Get the modified data from the text area
        modified_data = self.text_area.get(1.0, tk.END).strip()
        
        if not modified_data:
            messagebox.showwarning("Warning", "No changes made to the data.")
            return
        
        try:
            # Compress the modified data
            compressed_data = compress_deflate(modified_data)
            
            if not compressed_data:
                messagebox.showerror("Error", "Failed to compress data.")
                return
            
            # Ask for save path
            save_path = filedialog.asksaveasfilename(
                defaultextension=".jkr",
                filetypes=[("Save Files", "*.jkr")],
                initialfile=os.path.basename(self.current_file)
            )
            
            if save_path:
                with open(save_path, 'wb') as file:
                    file.write(compressed_data)
                
                filename = os.path.basename(save_path)
                messagebox.showinfo("Success", "File saved successfully.")
                self.status_label.config(text=f"Saved file: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save the modified file: {e}")
    
    """
    The 'Find' button function
    """

    def find_text(self):
        # Create Find Window with improved styling
        find_window = tk.Toplevel(self.root)
        find_window.title("Find Text")
        find_window.geometry("300x150")
        find_window.configure(bg=self.bg_color)
        find_window.resizable(False, False)
        
        # Center the window
        find_window.transient(self.root)
        find_window.grab_set()
        
        # Add padding
        container = ttk.Frame(find_window, style="TFrame")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(container, text="Enter keyword:", style="TLabel").pack(pady=5)
        
        find_entry = ttk.Entry(container, width=30)
        find_entry.pack(pady=5)
        find_entry.focus_set()
        
        def search():
            self.text_area.tag_remove("highlight", "1.0", tk.END)
            keyword = find_entry.get()
            
            if not keyword:
                return
            
            start_pos = "1.0"
            count = 0
            
            while True:
                start_pos = self.text_area.search(keyword, start_pos, stopindex=tk.END, nocase=True)
                if not start_pos:
                    break
                
                end_pos = f"{start_pos}+{len(keyword)}c"
                self.text_area.tag_add("highlight", start_pos, end_pos)
                start_pos = end_pos
                count += 1
            
            self.text_area.tag_config("highlight", background=self.highlight_color, foreground="black")
            
            if count > 0:
                self.status_label.config(text=f"Found {count} matches for '{keyword}'")
            else:
                self.status_label.config(text=f"No matches found for '{keyword}'")
            
            find_window.destroy()
        
        # Button frame
        button_frame = ttk.Frame(container, style="TFrame")
        button_frame.pack(pady=10)
        
        find_button = tk.Button(button_frame, text="Find", 
                               command=search,
                               bg=self.button_color, fg=self.button_text_color,
                               font=("Arial", 10), padx=10, pady=2,
                               relief="flat", borderwidth=0)
        find_button.pack(side="left", padx=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", 
                                 command=find_window.destroy,
                                 bg="#cccccc", fg="black",
                                 font=("Arial", 10), padx=10, pady=2,
                                 relief="flat", borderwidth=0)
        cancel_button.pack(side="left", padx=5)
        
        # Bind Enter key to search
        find_entry.bind("<Return>", lambda event: search())
    

    def edit_ante(self):
        self.quick_edit_variable("ante", "Ante")        # Quick edit ante function
    

    def quick_edit_variable(self, variable, display_name):
        if not self.imported_data:
            messagebox.showerror("Error", "No file loaded to edit.")   # If no file is loaded
            return
        
        # Create edit window with improved styling
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit {display_name}")
        edit_window.geometry("300x150")
        edit_window.configure(bg=self.bg_color)
        edit_window.resizable(False, False)
        
        # Center the window
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Add padding
        container = ttk.Frame(edit_window, style="TFrame")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(container, text=f"Enter new {display_name} value:", style="TLabel").pack(pady=5)
        
        value_entry = ttk.Entry(container, width=30)
        value_entry.pack(pady=5)
        value_entry.focus_set()
        
        """
        All changes will be applied to the raw data directly
        """
        
        def apply_changes():
            try:
                new_value = int(value_entry.get())
                
                # Update the variable in the data
                updated_data = self.update_variable(self.imported_data, variable, new_value)
                
                if updated_data:
                    # Update text area and imported data
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, updated_data)
                    self.imported_data = updated_data
                    
                    # Update preview
                    self.preview_text.config(state="normal")
                    self.preview_text.delete(1.0, tk.END)
                    preview_content = updated_data[:500] + "..." if len(updated_data) > 500 else updated_data
                    self.preview_text.insert(tk.END, preview_content)
                    self.preview_text.config(state="disabled")
                    
                    # Update status
                    self.status_label.config(text=f"{display_name} value updated successfully!")
                    
                    # Close window
                    edit_window.destroy()
                else:
                    messagebox.showerror("Error", f"Failed to update {display_name} value.")
            except ValueError:
                messagebox.showerror("Error", "Invalid input! Please enter a valid number.")
        
        # Button frame
        button_frame = ttk.Frame(container, style="TFrame")
        button_frame.pack(pady=10)
        
        apply_button = tk.Button(button_frame, text="Apply", 
                                command=apply_changes,
                                bg=self.button_color, fg=self.button_text_color,
                                font=("Arial", 10), padx=10, pady=2,
                                relief="flat", borderwidth=0)
        apply_button.pack(side="left", padx=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", 
                                 command=edit_window.destroy,
                                 bg="#cccccc", fg="black",
                                 font=("Arial", 10), padx=10, pady=2,
                                 relief="flat", borderwidth=0)
        cancel_button.pack(side="left", padx=5)
        
        # Bind Enter key to apply
        value_entry.bind("<Return>", lambda event: apply_changes())
    
    def update_variable(self, decompressed_data, variable, value):
        pattern = rf'(\["{variable}"\]=)\d+'
        modified_data = re.sub(pattern, lambda m: f'["{variable}"]={value}', decompressed_data)
        return modified_data
    
    def open_save_editor(self):
        if not self.imported_data:
            messagebox.showerror("Error", "No file loaded to edit.")
            return
        
        # Create a new window for the save editor with improved styling
        editor_window = tk.Toplevel(self.root)
        editor_window.title("Save Editor")
        editor_window.geometry("400x600")
        editor_window.configure(bg=self.bg_color)
        
        # Try to set icon
        try:
            editor_window.iconbitmap("icon.ico")
        except:
            pass
        
        # Center the window
        editor_window.transient(self.root)
        editor_window.grab_set()
        
        # Create scrollable frame
        main_frame = ttk.Frame(editor_window, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        
        scrollable_frame = ttk.Frame(canvas, style="TFrame")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Header
        header_label = ttk.Label(scrollable_frame, text="Edit Save Data", 
                                style="Header.TLabel")
        header_label.pack(pady=(0, 15))
        
        # Create entry fields
        entries = {}
        variables = [
            ("round", "Round"),
            ("ante", "Ante"),
            ("win_ante", "Win Ante"),
            ("discards", "Discards"),
            ("hands", "Hands"),
            ("dollars", "Money"),
            ("reroll_cost", "Reroll Cost"),
            ("max_jokers", "Joker Limit"),
            ("consumable_slots", "Consumable Slots"),
            ("bankrupt_at", "Bankrupt At"),
            ("hand_size", "Hand Size")
        ]
        
        for var, display in variables:
            frame = ttk.Frame(scrollable_frame, style="TFrame")
            frame.pack(fill="x", pady=5)
            
            label = ttk.Label(frame, text=f"{display}:", style="TLabel", width=15)
            label.pack(side="left", padx=5)
            
            entry = ttk.Entry(frame, width=20)
            entry.pack(side="left", padx=5, fill="x", expand=True)
            
            entries[var] = entry
        
        # Function to save changes
        def save_changes():
            try:
                # Get values from entries
                values = {}
                for var, entry in entries.items():
                    if entry.get():  # Only update if entry has a value
                        values[var] = int(entry.get())
                
                if not values:
                    messagebox.showinfo("Info", "No changes made.")
                    return
                
                # Update variables in data
                updated_data = self.imported_data
                for var, value in values.items():
                    updated_data = self.update_variable(updated_data, var, value)
                
                if updated_data:
                    # Update text area and imported data
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, updated_data)
                    self.imported_data = updated_data
                    
                    # Update preview
                    self.preview_text.config(state="normal")
                    self.preview_text.delete(1.0, tk.END)
                    preview_content = updated_data[:500] + "..." if len(updated_data) > 500 else updated_data
                    self.preview_text.insert(tk.END, preview_content)
                    self.preview_text.config(state="disabled")
                    
                    # Close window
                    editor_window.destroy()
                    
                    # Update status
                    self.status_label.config(text="Changes saved successfully.")
                else:
                    messagebox.showerror("Error", "Failed to update values.")
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter valid integers.")
        
        # Save button
        save_button = tk.Button(scrollable_frame, text="Save Changes", 
                               command=save_changes,
                               bg=self.button_color, fg=self.button_text_color,
                               font=("Arial", 11, "bold"), padx=15, pady=5,
                               relief="flat", borderwidth=0)
        save_button.pack(pady=20)
        
        # Cancel button
        cancel_button = tk.Button(scrollable_frame, text="Cancel", 
                                 command=editor_window.destroy,
                                 bg="#cccccc", fg="black",
                                 font=("Arial", 11), padx=15, pady=5,
                                 relief="flat", borderwidth=0)
        cancel_button.pack(pady=(0, 10))

# Main application
if __name__ == "__main__":
    root = Tk()
    app = SaveFileEditor(root)
    root.mainloop()

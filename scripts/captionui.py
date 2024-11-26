import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class CaptionEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Caption Editor")
        self.root.geometry("1800x1200")  # Increased window size
        
        self.image_label = tk.Label(root)
        self.image_label.grid(row=0, column=0, padx=20, pady=20)
        
        self.caption_text = tk.Text(root, wrap=tk.WORD, height=40, width=100, font=("Ubuntu Sans", 16))
        self.caption_text.grid(row=0, column=1, padx=20, pady=20)
        
        self.save_button = tk.Button(root, text="Save Caption", command=self.save_caption)
        self.save_button.grid(row=1, column=1, sticky=tk.W, padx=20, pady=10)
        
        self.load_button = tk.Button(root, text="Load Directory", command=self.load_directory)
        self.load_button.grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)
        
        self.image_files = []
        self.current_index = -1

        self.root.bind("<Up>", self.previous_image)
        self.root.bind("<Down>", self.next_image)

    def load_directory(self):
        folder_path = filedialog.askdirectory(title="Select Directory")
        
        if not folder_path:
            return
        
        self.image_files = []
        for root_dir, subdirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(root_dir, file)
                    caption_path = os.path.splitext(image_path)[0] + ".txt"
                    if os.path.exists(caption_path):
                        self.image_files.append((image_path, caption_path))
        
        if self.image_files:
            self.current_index = 0
            self.display_image_and_caption()
        else:
            messagebox.showwarning("No images", "No images with captions found in the selected directory.")

    def display_image_and_caption(self):
        if self.current_index < 0 or self.current_index >= len(self.image_files):
            return
        
        image_path, caption_path = self.image_files[self.current_index]
        
        image = Image.open(image_path)
        image.thumbnail((1024, 1024))  # Fit to 512x512 while maintaining aspect ratio
        img_display = ImageTk.PhotoImage(image)
        self.image_label.configure(image=img_display)
        self.image_label.image = img_display
        
        with open(caption_path, "r") as file:
            caption = file.read()
        
        self.caption_text.delete(1.0, tk.END)
        self.caption_text.insert(tk.END, caption)

    def save_caption(self):
        if self.current_index < 0 or self.current_index >= len(self.image_files):
            return
        
        image_path, caption_path = self.image_files[self.current_index]
        
        new_caption = self.caption_text.get(1.0, tk.END).strip()
        if not new_caption:
            messagebox.showwarning("Empty Caption", "Caption cannot be empty.")
            return
        
        with open(caption_path, "w") as file:
            file.write(new_caption)
        
        messagebox.showinfo("Saved", "Caption saved successfully.")

    def previous_image(self, event=None):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_image_and_caption()

    def next_image(self, event=None):
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.display_image_and_caption()

if __name__ == "__main__":
    root = tk.Tk()
    app = CaptionEditorApp(root)
    root.mainloop()

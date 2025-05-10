import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage  # Para trabalhar com imagens nos botões

class JarvisGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jarvis Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg='#1e1e1e')

        # Title Label
        self.title_label = tk.Label(
            self.root,
            text="Jarvis - Assistente Pessoal",
            font=("Helvetica", 20, "bold"),
            fg="#ffffff",
            bg="#1e1e1e"
        )
        self.title_label.pack(pady=20)

        # Output Text Area
        self.output_text = tk.Text(
            self.root,
            height=20,
            width=80,
            bg="#2d2d2d",
            fg="#ffffff",
            insertbackground="#ffffff",
            font=("Helvetica", 12)
        )
        self.output_text.pack(padx=20, pady=10)

        # Frame para organizar os botões
        self.button_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.button_frame.pack(pady=10)

        # Text Input Entry
        self.input_entry = tk.Entry(
            self.root,
            width=60,
            font=("Helvetica", 14),
            bg="#3c3f41",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.input_entry.pack(pady=10)

        # Botão para Falar com Imagem
        self.listen_button_image = PhotoImage(file=r"C:\Users\adria\PycharmProjects\PythonProject3\assets\frame0\button_2.png")  # Substitua pelo caminho correto
        self.listen_button = tk.Button(
            self.button_frame,
            image=self.listen_button_image,
            command=self.trigger_listening,
            bg="#1e1e1e",
            relief="flat"
        )
        self.listen_button.grid(row=0, column=0, padx=10)

        # Botão para Enviar Texto com Imagem
        self.submit_button_image = PhotoImage(file=r"C:\Users\adria\PycharmProjects\PythonProject3\assets\frame0\button_1.png")  # Substitua pelo caminho correto
        self.submit_button = tk.Button(
            self.button_frame,
            image=self.submit_button_image,
            command=self.submit_text,
            bg="#1e1e1e",
            relief="flat"
        )
        self.submit_button.grid(row=0, column=1, padx=10)

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def trigger_listening(self):
        from main import start_listening  # Import the function to start listening
        start_listening()

    def submit_text(self):
        from main import handle_text_input  # Import the function to handle text input
        user_input = self.input_entry.get()
        self.input_entry.delete(0, tk.END)  # Clear the input field
        handle_text_input(user_input)  # Pass the text input to the main logic

    def update_output(self, text):
        self.output_text.insert(tk.END, f"{text}\n")
        self.output_text.see(tk.END)

    def _on_closing(self):
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def update_ui_output(text):
    global gui
    if gui:
        gui.update_output(text)


# Global instance for cross-module access
gui = JarvisGUI()

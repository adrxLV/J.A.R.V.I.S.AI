from customtkinter import *
from PIL import Image  # To load images into CTkImage


class JarvisGUI:
    def __init__(self):
        # Initial configuration of the main window
        set_appearance_mode("Dark")  # Enables dark mode for modern look
        set_default_color_theme("blue")  # Sets default UI color theme
        self.root = CTk()  # CTk is a themed replacement for tkinter.Tk
        self.root.title("Jarvis Assistant")
        self.root.geometry("800x600")

        # Grid configuration for responsive layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=6)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Header label with a welcome message
        self.title_label = CTkLabel(
            self.root,
            text="Good morning, Adriano\nWhat can I help you with today?",
            font=CTkFont(size=22, weight="bold"),
            justify="center"
        )
        self.title_label.grid(row=0, column=0, pady=20, sticky="n")

        # Textbox used to display assistant output
        self.output_text = CTkTextbox(
            self.root,
            height=300,
            width=700,
            font=CTkFont(size=14),
            wrap="word",
            state="disabled",  # Read-only mode
            fg_color="#1a1a1a",  # Dark background
            text_color="white",
            corner_radius=10,
            border_width=1,
            border_color="gray"
        )
        self.output_text.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Input frame holds the entry field and the buttons
        self.input_frame = CTkFrame(self.root, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=5)
        self.input_frame.grid_columnconfigure(2, weight=1)

        # Load microphone and send button icons
        self.microphone_icon = CTkImage(
            light_image=Image.open("assets/frame0/button_2.png"),
            size=(20, 20)
        )
        self.send_icon = CTkImage(
            light_image=Image.open("assets/frame0/button_1.png"),
            size=(20, 20)
        )

        # Button to trigger voice listening function
        self.listen_button = CTkButton(
            self.input_frame,
            image=self.microphone_icon,
            text="",
            command=self.trigger_listening,
            font=CTkFont(size=14, weight="bold"),
            width=50,
            height=50,
            corner_radius=25,  # Creates a circular button
            fg_color="#0078d7"
        )
        self.listen_button.grid(row=0, column=0, padx=10, pady=5)

        # Text entry field for manual user input
        self.input_entry = CTkEntry(
            self.input_frame,
            placeholder_text="Type your message here...",
            font=CTkFont(size=14),
            height=40,
            corner_radius=10,
            border_width=2,
            border_color="gray"
        )
        self.input_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Submit button sends the text input to backend logic
        self.submit_button = CTkButton(
            self.input_frame,
            text="Send",
            image=self.send_icon,
            compound="left",
            command=self.submit_text,
            font=CTkFont(size=14, weight="bold"),
            width=100,
            height=40,
            corner_radius=10
        )
        self.submit_button.grid(row=0, column=2, padx=10, pady=5)

        # Handle graceful shutdown when user closes the window
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def trigger_listening(self):
        from main import start_listening  # Calls external voice input function
        start_listening()

    def submit_text(self):
        from main import handle_text_input  # Calls external text input function
        user_input = self.input_entry.get()
        self.input_entry.delete(0, END)  # Clear entry after submission
        handle_text_input(user_input)  # Pass user input to main logic

    def update_output(self, text):
        # Enables text editing, appends new message, and disables editing again
        self.output_text.configure(state="normal")
        self.output_text.insert(END, f"{text}\n")
        self.output_text.yview(END)  # Scrolls to the latest line
        self.output_text.configure(state="disabled")

    def _on_closing(self):
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def update_ui_output(text):
    global gui
    if gui:
        gui.update_output(text)


# Global GUI instance accessible from other modules
gui = JarvisGUI()

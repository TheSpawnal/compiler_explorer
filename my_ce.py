import tkinter as tk
from tkinter import scrolledtext
from subprocess import Popen, PIPE
import threading
import time
import re

class CppAssemblyViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("C++ to Assembly Viewer")
        self.root.geometry('800x600')  # Set initial size of the window
        self.root.config(bg="#333")

        # Initialize variables
        self.compiler = tk.StringVar(value="g++")
        self.opt_level = tk.StringVar(value="-O0")
        self.setup_ui()

        # Start the update thread
        threading.Thread(target=self.update_assembly, daemon=True).start()

    def setup_ui(self):
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Input text widget for C++ code
        self.text_input = scrolledtext.ScrolledText(self.root, bg="#222", fg="#ddd", insertbackground="white")
        self.text_input.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        # Output text widget for assembly
        self.text_output = scrolledtext.ScrolledText(self.root, bg="#222", fg="#ddd", state=tk.DISABLED)
        self.text_output.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.text_output.tag_configure("register", foreground="#40E0D0")  # Turquoise color for registers

        # Compiler and optimization level selection
        tk.OptionMenu(self.root, self.compiler, "g++", "clang").grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        tk.OptionMenu(self.root, self.opt_level, "-O0", "-O1", "-O2", "-O3").grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        

    def update_assembly(self):
        while True:
            time.sleep(0.5)
            code = self.text_input.get("1.0", tk.END)
            if code.strip() == "":
                self.display_output("")
                continue
            self.compile_code(code)

    def highlight_registers(self, text):
        # Example register patterns for x86/x64 architectures, adjust the list according to target architecture
        registers = r"\b(rax|rbx|rcx|rdx|rsi|rdi|r8|r9|r10|r11|r12|r13|r14|r15|eax|ebx|ecx|edx|esi|edi|esp|ebp)\b"
        start = "1.0"
        while True:
            match = re.search(registers, text, re.IGNORECASE)
            if not match:
                break
            start = self.text_output.search(match.group(), start, tk.END)
            if not start:
                break
            end = f"{start}+{len(match.group())}c"
            self.text_output.tag_add("register", start, end)
            start = end

    def compile_code(self, code):
        cmd = [self.compiler.get(), "-x", "c++", "-S", "-masm=intel", "-o-", "-", self.opt_level.get()]
        process = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)
        stdout, stderr = process.communicate(input=code)
        if stderr:
            self.display_output("Error:\n" + stderr)
        else:
            self.display_output(stdout)

    def display_output(self, text):
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete("1.0", tk.END)
        self.text_output.insert(tk.END, text)
        self.highlight_registers(text)
        self.text_output.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = CppAssemblyViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()

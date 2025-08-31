import tkinter as tk
from tkinter import messagebox, filedialog
import math
import ast
import operator as op
import binascii

class SafeEval:
    operators = {
        ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
        ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg,
        ast.Mod: op.mod, ast.FloorDiv: op.floordiv,
    }
    functions = {
        'sqrt': math.sqrt, 'log': math.log10, 'ln': math.log,
        'sin': lambda x: math.sin(math.radians(x)),
        'cos': lambda x: math.cos(math.radians(x)),
        'tan': lambda x: math.tan(math.radians(x)),
        'abs': abs, 'fact': math.factorial,
        'exp': math.exp,
    }
    def eval_expr(self, expr):
        return self._eval(ast.parse(expr, mode='eval').body)
    def _eval(self, node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return self.operators[type(node.op)](self._eval(node.left), self._eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return self.operators[type(node.op)](self._eval(node.operand))
        elif isinstance(node, ast.Call):
            func_name = node.func.id
            if func_name in self.functions:
                args = [self._eval(arg) for arg in node.args]
                return self.functions[func_name](*args)
            else:
                raise Exception("Unsupported function")
        else:
            raise TypeError(node)

class AdvancedCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Samyuktha's Advanced Scientific Calculator")
        self.geometry("450x620")
        self.eval_engine = SafeEval()
        self.dark_mode = True
        self.history = []
        self.last_answer = None
        self.expression = ""
        self.create_widgets()
        self.apply_theme()
        self.bind('<Return>', lambda e: self.calculate())

    def create_widgets(self):
        self.display = tk.Text(self, font=("Consolas", 24), height=2, width=24,
                               padx=10, pady=5, bd=0, relief="flat")
        self.display.grid(row=0, column=0, columnspan=5, padx=10, pady=15, sticky="nsew")
        self.display.config(state='disabled')

        buttons = [
            ['7', '8', '9', '/', 'sqrt'],
            ['4', '5', '6', '*', 'log'],
            ['1', '2', '3', '-', 'sin'],
            ['0', '.', 'Ans', '+', 'cos'],
            ['(', ')', 'pi', '^', 'tan'],
            ['Clear', 'Del', 'History', 'Theme', 'Export']
        ]

        self.actions = {
            'Clear': self.clear, 'Del': self.delete_last, 'History': self.show_history,
            'Theme': self.toggle_theme, 'Ans': self.insert_last_answer,
            'pi': lambda: self.insert_text(str(round(math.pi, 8))),
            '^': lambda: self.insert_text('**'), 'Export': self.export_data
        }

        for r, row in enumerate(buttons, start=1):
            for c, label in enumerate(row):
                color_bg, color_fg = self.get_button_colors(label)
                btn = tk.Button(self, text=label, font=("Arial", 16), width=6, height=3,
                                bg=color_bg, fg=color_fg, activebackground="#5e4d44",
                                command=self.get_action(label))
                btn.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)

        for i in range(5):
            self.grid_columnconfigure(i, weight=1)
        for i in range(7):
            self.grid_rowconfigure(i, weight=1)

    def get_button_colors(self, label):
        if self.dark_mode:
            bg_main = "#3e322f"
            bg_func = "#584739"
            bg_special = "#6a4e42"
            fg_text = "#ffffff"
        else:
            bg_main = "#d2cbb7"
            bg_func = "#b59d7a"
            bg_special = "#7a684a"
            fg_text = "#3e322f"

        if label in ('sqrt', 'log', 'sin', 'cos', 'tan'):
            return bg_func, fg_text
        elif label in ('Ans', 'Clear', 'Del', 'History', 'Export', 'Theme'):
            return bg_special, fg_text
        else:
            return bg_main, fg_text

    def get_action(self, label):
        if label in self.actions:
            return self.actions[label]
        elif label in ('sqrt', 'log', 'sin', 'cos', 'tan'):
            return lambda l=label: self.insert_text(f"{l}(")
        else:
            return lambda l=label: self.insert_text(l)

    def update_display(self):
        self.display.config(state='normal')
        self.display.delete("1.0", tk.END)
        expr_to_show = self.expression if self.expression.strip() != "" else "0"
        answer_line = str(self.last_answer) if self.last_answer is not None else ""

        # Insert expression and answer with styled tags
        self.display.insert("1.0", expr_to_show + "\n")
        self.display.insert("2.0", "= " + answer_line)

        self.display.tag_configure("expr", font=("Consolas", 18), foreground="#888888")  # smaller, grey
        self.display.tag_configure("answer", font=("Consolas", 30, "bold"), foreground="#ffffff")  # larger, white

        self.display.tag_add("expr", "1.0", "1.end")
        self.display.tag_add("answer", "2.0", "2.end")

        self.display.config(state='disabled')

    def insert_text(self, text):
        self.expression += text
        self.update_display()

    def clear(self):
        self.expression = ""
        self.last_answer = None
        self.update_display()

    def delete_last(self):
        self.expression = self.expression[:-1]
        self.update_display()

    def insert_last_answer(self):
        if self.last_answer is not None:
            self.expression += str(self.last_answer)
            self.update_display()

    def show_history(self):
        hist_win = tk.Toplevel(self)
        hist_win.title("Calculation History")
        hist_text = tk.Text(hist_win, height=15, width=40, font=("Courier New", 12))
        hist_text.pack(padx=10, pady=10)
        for entry in reversed(self.history[-50:]):
            hist_text.insert(tk.END, entry + "\n")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            self.bg_color = "#1e1e1e"
            self.display_bg = "#000000"
            self.display_fg = "#ffffff"
        else:
            self.bg_color = "#f7f5f0"
            self.display_bg = "#ffffff"
            self.display_fg = "#3e322f"

        self.configure(bg=self.bg_color)
        self.display.config(bg=self.display_bg, fg=self.display_fg, insertbackground=self.display_fg)

        for widget in self.winfo_children():
            if isinstance(widget, tk.Button):
                text = widget.cget("text")
                bg, fg = self.get_button_colors(text)
                widget.config(bg=bg, fg=fg, activebackground="#5e4d44")

        self.update_display()

    def calculate(self):
        expr = self.expression.strip()
        if expr == "":
            return
        try:
            result = self.eval_engine.eval_expr(expr)
            self.last_answer = result
            self.history.append(f"{expr} = {result}")
            self.expression = str(result)
            self.update_display()
        except Exception:
            self.last_answer = None
            self.expression = "Error"
            self.update_display()

    def export_data(self):
        option = messagebox.askquestion("Export Option", "Export Last Answer? (Yes)\nExport Full Calculation History? (No)")
        if option == 'yes':
            data = str(self.last_answer) if self.last_answer is not None else "No answer to export."
        else:
            data = "\n".join(self.history) if self.history else "No history to export."

        formats = [("Standard Text (*.txt)", "*.txt"), ("Binary File (*.bin)", "*.bin"), ("Hexadecimal File (*.hex)", "*.hex")]
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=formats)
        if not file_path:
            return

        try:
            if file_path.endswith(".bin"):
                with open(file_path, "wb") as f:
                    f.write(data.encode('utf-8'))
            elif file_path.endswith(".hex"):
                with open(file_path, "w") as f:
                    f.write(binascii.hexlify(data.encode('utf-8')).decode('utf-8'))
            else:
                with open(file_path, "w") as f:
                    f.write(data)
            messagebox.showinfo("Export Successful", f"Data exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error: {str(e)}")

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    calc = AdvancedCalculator()
    calc.run()

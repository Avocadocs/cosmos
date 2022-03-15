import tkinter as tk
from tkinter import ttk
from constants import *
import re
from ctypes import windll


class CodeEditor(tk.Text):
    """Create code editor widget."""

    def __init__(self, master, language=None, theme:dict=None, **kwargs):
        
        tk.Text.__init__(self, master, **kwargs)
        self.configure(
            background='#2D2B55',
            fg='#CFCFCF',
            insertbackground='#E8C205',
            selectbackground='#7448AF',
            font=('Consolas', 10),
            undo=True,
            insertwidth=4,
            tabs=44,
            tabstyle='wordprocessor',
            wrap=tk.NONE,
            insertofftime=600,
            insertontime=600
        )
        
        self.lines = tk.Text(master)
        self.lines.configure(
            background='#28284E',
            fg='#A599E9',
            font=('Consolas', 10),
            width=8
        )

        self.operators = ['if', 'else', 'for', 'in', 'while', 'try', 'except', 'def', 'import', 'as', 'from', 'elif', 'class']
        self.operations = ['+', '-', '*', '/', '=', '<', '>']
        self.numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'True', 'False']
        self.special = ["'*'", '"*"']
        self.types = ['int', 'bool', 'float', 'str', 'dict', 'list']

        self.tag_configure(OPERATOR, foreground='#FF9D00')
        self.tag_configure(OPERATION, foreground='#FF9D00')
        self.tag_configure(METHOD, foreground='#FAC337')
        self.tag_configure(VARIABLE, foreground='#9EFFFF')
        self.tag_configure(TYPE, foreground='#80FFBB')
        self.tag_configure(STRING, foreground='#A5FF90')
        self.tag_configure(NUMBER, foreground='#FF628C')

        self.tag_configure(LINE, foreground='')
        self.tag_configure(ACTIVELINE, foreground='')

        self.bind('<KeyRelease>', lambda e: self.syntax(self, OPERATOR, self.operators, True))
        self.bind('<KeyRelease>', lambda e: self.syntax(self, OPERATION, self.operations), add='+')
        self.bind('<KeyRelease>', lambda e: self.syntax(self, NUMBER, self.numbers), add='+')
        self.bind('<KeyRelease>', lambda e: self.find_string(self, STRING, self.special), add='+')
        self.bind('<KeyRelease>', lambda e: self.syntax(self, TYPE, self.types, True), add='+')
        self.bind('<KeyRelease>', lambda e: self.syntax(self, METHOD, self.types, False, '.\w+(?=\s?\()'), add='+')
        self.bind('<KeyRelease>', lambda e: self.syntax(self, VARIABLE, self.types, True, '\w+(?=\s?=)'), add='+')

        self.bind('<KeyRelease>', self.auto_insert, add='+')
        self.bind('<KeyRelease>', lambda event: self.update_lines(event, self.lines), add='+')
        self.bind('<KeyRelease>', self.update, add='+')

        self.lines.pack(anchor=tk.NW, side=tk.LEFT, fill=tk.Y)
        self.pack(anchor=tk.NW, side=tk.LEFT, fill=tk.BOTH, expand=1)


    def syntax(self, widget, tag, word_list, regex=False, expression=None, all_text=False):
        """Color words using language syntax."""
    
        if all_text == True:
            start = '1.0'
            end = tk.END
        else:
            start = int(widget.index(tk.INSERT).split('.')[0])
            end = str(f'{start+1}.0')
            start = str(f'{start}.0')
        widget.tag_remove(tag, start, end)
   
        countvar = tk.IntVar()
        if expression:
            word_list = re.findall(expression, widget.get(start, end))

        for word in word_list:
            if all_text == True:
                start = '1.0'
            else:
                start = int(widget.index(tk.INSERT).split('.')[0])
                start = str(f'{start}.0')
            if regex == True:
                pattern = r'\m{}\M'.format(word)
            else: 
                pattern = word
            while widget.compare(start, '<=', end):
                start = widget.search(pattern, start, end, count=countvar, regexp=regex)
                if start:
                    pos_end = widget.index('{} + {} chars'.format(start, countvar.get()))
                    widget.tag_add(tag, start, pos_end)
                    start = pos_end
                else:
                    break

    def find_string(self, widget, tag, word_list, all_text=False):
        """Find all whole words in word_list and apply the given tag"""

        if all_text == True:
            start= '1.0'
            end=tk.END
        else:
            start = int(widget.index(tk.INSERT).split('.')[0])
            end = str(f'{start+1}.0')
            start = str(f'{start}.0')
        widget.tag_remove(tag, start, end)

        countvar = tk.IntVar()
        test = re.findall('"([^"]*)"', widget.get(start, end))
        word_list = []
        for word in test:
            word_list.append('"'+word+'"')
        for word in word_list:
            if all_text == True:
                start='1.0'
            else:
                start = int(widget.index(tk.INSERT).split('.')[0])
                start = str(f'{start}.0')

            while widget.compare(start, "<=", end):
                start = widget.search(word, start, end, count=countvar, regexp=True)
                if start:
                    pos_end = widget.index("{} + {} chars".format(start, countvar.get()))
                    widget.tag_add(tag, start, pos_end)
                    start = pos_end
                else:
                    break


    def update(self, event):
        if event.keycode == 86:
            self.syntax(self, OPERATOR, self.operators, True, all_text=True)
            self.syntax(self, OPERATION, self.operations, all_text=True)
            self.syntax(self, NUMBER, self.numbers, all_text=True)
            self.syntax(self, TYPE, self.types, True, all_text=True)
            self.syntax(self, METHOD, self.types, False, '.\w+(?=\s?\()', all_text=True)
            self.syntax(self, VARIABLE, self.types, True, '\w+(?=\s?=)', all_text=True)
            self.find_string(self, STRING, self.special, all_text=True)


    def update_lines(self, event, widget):
        if event.keycode == 8 or event.keycode == 13 or event.keycode == 86:
            widget.configure(state='normal')
            widget.delete('1.0', 'end')
            widget.tag_remove('line', '1.0', tk.END)
            lines = int(self.index('end').split('.')[0])
            for i in range(1, lines):
                widget.insert(tk.END, str(i)+'\n')
            widget.configure(state='disabled')
            widget.tag_add('line', '1.0', tk.END)


    def auto_insert(self, event):
        if event.char == '"':
            pos = self.index(tk.INSERT)
            self.insert(tk.INSERT, '"')
            self.mark_set(tk.INSERT, pos)
        elif event.char == "'":
            pos = self.index(tk.INSERT)
            self.insert(tk.INSERT, "'")
            self.mark_set(tk.INSERT, pos)
        elif event.char == '(':
            pos = self.index(tk.INSERT)
            self.insert(tk.INSERT, ')')
            self.mark_set(tk.INSERT, pos)


if __name__ == '__main__':

    windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()

    CodeEditor(root)

    root.mainloop()

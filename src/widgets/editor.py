import tkinter as tk
from tkinter import ttk
import re
from ctypes import windll


class CodeEditor(tk.Frame):
    """Create code editor widget."""

    def __init__(self, master, language=None, theme:dict=None, **kwargs):
        
        tk.Frame.__init__(self, master, **kwargs)
        self.editor = tk.Text(self)

        yscrollbar = ttk.Scrollbar(self.editor, command=self.scrolly, cursor=r'@cursors\\aero_arrow.cur')
        xscrollbar = ttk.Scrollbar(self.editor, command=self.scrollx, orient='horizontal', cursor=r'@cursors\\aero_arrow.cur')

        self.editor.configure(
            background='#2D2B55',
            fg='#CFCFCF',
            insertbackground='#E8C205',
            selectbackground='#7448AF',
            font=('Consolas', 10),
            undo=True,
            insertwidth=3,
            tabs=44,
            wrap=tk.NONE,
            insertofftime=600,
            insertontime=600,
            xscrollcommand=xscrollbar.set,
            yscrollcommand=yscrollbar.set
        )

        peer = tk.Text(self)
        peer.destroy()      # the underlying tk widget gets replaced with the peer
        self.editor.peer_create(peer,
            background='#2D2B55',
            fg='#CFCFCF',
            insertbackground='#E8C205',
            selectbackground='#7448AF',
            font=('Consolas', 2),
            undo=True,
            insertwidth=3,
            tabs=44,
            wrap=tk.NONE,
            insertofftime=600,
            insertontime=600,
            xscrollcommand=xscrollbar.set,
            yscrollcommand=yscrollbar.set,
            state='disabled',
            cursor=r'@cursors\\aero_arrow.cur'
        )
        
        
        self.lines = tk.Text(self)
        self.lines.insert('1.0', 1)
        self.lines.configure(
            background='#28284E',
            selectbackground='#28284E',
            selectforeground='#A599E9',
            fg='#A599E9',
            font=('Consolas', 10),
            width=6,
            cursor=r'@cursors\\aero_arrow.cur',
            state='disabled',
            padx=10
        )

        xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.operators = ['if', 'else', 'for', 'in', 'while', 'try', 'except', 'def', 'import', 'as', 'from', 'elif', 'class', 'lambda', 'and']
        self.operations = ['+', '-', '*', '/', '=', '<', '>']
        self.numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'True', 'False']
        self.special = ["'*'", '"*"']
        self.types = ['int', 'bool', 'float', 'str', 'dict', 'list']

        self.editor.tag_configure('operator', foreground='#FF9D00')
        self.editor.tag_configure('operation', foreground='#FF9D00')
        self.editor.tag_configure('method', foreground='#FAC337')
        self.editor.tag_configure('variable', foreground='#9EFFFF')
        self.editor.tag_configure('type', foreground='#80FFBB')
        self.editor.tag_configure('string', foreground='#A5FF90')
        self.editor.tag_configure('number', foreground='#FF628C')

        self.editor.tag_configure('active', background='#1F1F41')

        self.lines.tag_configure('line', justify='right')
        self.lines.tag_configure('active', foreground='#C6C6C6')

        self.lines.tag_add('line', 1.0, tk.END)

        self.editor.bind('<KeyRelease>', lambda e: self.syntax(self.editor, 'operator', self.operators, True))
        self.editor.bind('<KeyRelease>', lambda e: self.syntax(self.editor, 'operation', self.operations), add='+')
        self.editor.bind('<KeyRelease>', lambda e: self.syntax(self.editor, 'number', self.numbers), add='+')
        self.editor.bind('<KeyRelease>', lambda e: self.find_string(self.editor, 'string', self.special), add='+')
        self.editor.bind('<KeyRelease>', lambda e: self.syntax(self.editor, 'type', self.types, True), add='+')
        self.editor.bind('<KeyRelease>', lambda e: self.syntax(self.editor, 'method', self.types, False, '\w+(?=\s?\()'), add='+')
        self.editor.bind('<KeyRelease>', lambda e: self.syntax(self.editor, 'variable', self.types, True, '\w+(?=\s?=)'), add='+')

        self.editor.bind('<KeyRelease>', lambda event: master.after_idle(self.update_lines), add='+')
        self.editor.bind('<Return>', self.update, add='+')
        self.editor.bind('<Return>', self.intedent, add='+')
        self.editor.bind('<Button-1>', lambda event:master.after_idle(self.active_line), add='+')
        self.editor.bind('<KeyRelease>', self.auto_insert, add='+')
        self.editor.bind('<BackSpace>', self.delete, add='+')
        #self.editor.bind('<Tab>', self.tab, add='+')
        

        self.lines.pack(anchor=tk.NW, side=tk.LEFT, fill=tk.Y)
        self.editor.pack(anchor=tk.NW, side=tk.LEFT, fill=tk.BOTH, expand=1)
        peer.pack(anchor=tk.NW, side=tk.LEFT, fill=tk.Y)

        
        #print(self.editor.edit_modified())


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

            while widget.compare(start, '<=', end):
                start = widget.search(word, start, end, count=countvar, regexp=True)
                if start:
                    pos_end = widget.index('{} + {} chars'.format(start, countvar.get()))
                    widget.tag_add(tag, start, pos_end)
                    start = pos_end
                else:
                    break


    def update(self, event):
        if event.keycode == 86:
            self.syntax(self.editor, 'operator', self.operators, True, all_text=True)
            self.syntax(self.editor, 'operation', self.operations, all_text=True)
            self.syntax(self.editor, 'number', self.numbers, all_text=True)
            self.syntax(self.editor, 'type', self.types, True, all_text=True)
            self.syntax(self.editor, 'method', self.types, False, '?.\w+(?=\s?\()', all_text=True)
            self.syntax(self.editor, 'variable', self.types, True, '\w+(?=\s?=)', all_text=True)
            self.find_string(self.editor, 'string', self.special, all_text=True)


    def update_lines(self):
        
        self.lines.configure(state='normal')
        self.lines.delete('1.0', 'end')
        self.lines.tag_remove('line', '1.0', tk.END)
        lines = int(self.editor.index('end').split('.')[0])
        for i in range(1, lines):
            self.lines.insert(tk.END, str(i)+'\n')
        self.lines.tag_add('line', '1.0', tk.END)
        self.lines.configure(state='disabled')
        


    def active_line(self):
       pass


    def intedent(self, event):
        line = self.editor.index(tk.INSERT)
        prevline = self.editor.index(tk.INSERT+'- 1 chars')
        content = self.editor.get(prevline, line)

        prev = self.editor.index(line+'linestart')
        end = self.editor.index(line+'lineend')
        line = self.getindex(prev, end)

        if content == ':' or content == '{':
            
            self.editor.insert(tk.INSERT, '\n\t')
            while self.editor.compare(line, '>', prev):
                self.editor.insert(tk.INSERT, '\t')
                prev = self.editor.index(prev+'+1c')
            return 'break'

        elif line != prev:

            self.editor.insert(tk.INSERT, '\n')
            while self.editor.compare(line, '>', prev):
                self.editor.insert(tk.INSERT, '\t')
                prev = self.editor.index(prev+'+1c')
            return 'break'


    def getindex(self, start, end):
        string = self.editor.get(start, end)
        for i in string:
            if i =='\t':
                start+='+1c'
        return self.editor.index(start)


    def tab(self, event):
        line = self.editor.index(tk.INSERT)

        prev = self.editor.index(line+"linestart")
        end = self.editor.index(line+"lineend")
        line = self.getindex(prev, end)
        print(line)
        while self.editor.compare(line, '>', prev):
            self.editor.insert(tk.INSERT, '\t')
            prev = self.editor.index(prev+'+1c')
        return 'break'


    def remove(self, event):
        if self.editor.get(tk.INSERT + 'linestart', tk.INSERT + 'lineend') == '   ':
            self.editor.delete(tk.INSERT + 'linestart', tk.INSERT + 'lineend')
            return 'break'
            

    def delete(self, event):
        if self.editor.get(tk.INSERT) == ')' and self.editor.get(tk.INSERT+' -1c') == '(':
            self.editor.delete(tk.INSERT, tk.INSERT+' +1c')
        elif self.editor.get(tk.INSERT) == '}' and self.editor.get(tk.INSERT+' -1c') == '{':
            self.editor.delete(tk.INSERT, tk.INSERT+' +1c')
        elif self.editor.get(tk.INSERT) == '"' and self.editor.get(tk.INSERT+' -1c') == '"':
            self.editor.delete(tk.INSERT, tk.INSERT+' +1c')
        elif self.editor.get(tk.INSERT) == "'" and self.editor.get(tk.INSERT+' -1c') == "'":
            self.editor.delete(tk.INSERT, tk.INSERT+' +1c')

    def auto_insert(self, event):
        if event.char == '{':
            print('{')
        elif event.char == '(':
            letter = self.editor.get(tk.INSERT, tk.INSERT+' +1c')
            print(letter)
            if letter.isalpha() == False:
                self.editor.insert(tk.INSERT, ')')
                self.editor.mark_set(tk.INSERT, tk.INSERT+' -1c')
        elif event.char == '"':
            letter = self.editor.get(tk.INSERT, tk.INSERT+' +1c')
            if letter.isalpha() == False:
                self.editor.insert(tk.INSERT, '"')
                self.editor.mark_set(tk.INSERT, tk.INSERT+' -1c')
        elif event.char == "'":
            letter = self.editor.get(tk.INSERT, tk.INSERT+' +1c')
            if letter.isalpha() == False:
                self.editor.insert(tk.INSERT, "'")
                self.editor.mark_set(tk.INSERT, tk.INSERT+' -1c')


    def scrollx(self, *args):
        self.editor.xview(*args)


    def scrolly(self, *args):
        self.editor.yview(*args)
        self.lines.yview(*args)


if __name__ == '__main__':

    windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    root.tk.call("encoding", "system", "utf-8")

    CodeEditor(root).pack(anchor=tk.NW, fill=tk.BOTH, expand=1)

    root.mainloop()

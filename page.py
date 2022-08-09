class Page:
    def __init__(self, lines, text):
        self.lines = lines
        self.text = text
    
    def add_line(self, line):
        self.lines.append(line)
    
    def add_text(self, position, text):
        self.text.append([position, text])
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import re
import os

class ConceptPaperPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, 'HealthLink: AI-Powered Telemedicine Platform - Concept Paper', align='C')
            self.ln(5)
            self.set_draw_color(52, 152, 219)
            self.line(10, 15, 200, 15)
            self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def chapter_title(self, title, level=1):
        if level == 1:
            self.add_page()
            self.set_font('Helvetica', 'B', 16)
            self.set_text_color(26, 82, 118)
            self.multi_cell(0, 10, title.upper())
            self.set_draw_color(26, 82, 118)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(6)
        elif level == 2:
            self.ln(4)
            self.set_font('Helvetica', 'B', 13)
            self.set_text_color(40, 116, 166)
            self.multi_cell(0, 8, title)
            self.ln(2)
        elif level == 3:
            self.ln(3)
            self.set_font('Helvetica', 'B', 11)
            self.set_text_color(52, 152, 219)
            self.multi_cell(0, 7, title)
            self.ln(2)
        elif level == 4:
            self.ln(2)
            self.set_font('Helvetica', 'BI', 10)
            self.set_text_color(80, 80, 80)
            self.multi_cell(0, 6, title)
            self.ln(1)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        # Replace special characters
        text = text.replace('→', '->')
        text = text.replace('◄', '<')
        text = text.replace('►', '>')
        text = text.replace('▼', 'v')
        text = text.replace('─', '-')
        text = text.replace('│', '|')
        text = text.replace('┌', '+')
        text = text.replace('┐', '+')
        text = text.replace('└', '+')
        text = text.replace('┘', '+')
        text = text.replace('├', '+')
        text = text.replace('┤', '+')
        text = text.replace('┬', '+')
        text = text.replace('┴', '+')
        text = text.replace('┼', '+')
        text = text.replace('✓', '[OK]')
        text = text.replace('☑', '[x]')
        text = text.replace('□', '[ ]')
        text = text.replace('📱', '[Phone]')
        text = text.replace('🔍', '[Search]')
        self.multi_cell(0, 5, text)
        self.ln(2)
        
    def bullet_point(self, text, indent=0):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        x = self.get_x() + indent
        self.set_x(x)
        # Replace special characters
        text = text.replace('→', '->')
        text = text.replace('✓', '[OK]')
        self.cell(5, 5, chr(149))  # bullet character
        self.multi_cell(0, 5, text.strip())
        self.ln(1)

    def code_block(self, code):
        self.set_font('Courier', '', 8)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(50, 50, 50)
        # Replace special characters
        code = code.replace('→', '->')
        code = code.replace('◄', '<')
        code = code.replace('►', '>')
        code = code.replace('▼', 'v')
        code = code.replace('─', '-')
        code = code.replace('│', '|')
        code = code.replace('┌', '+')
        code = code.replace('┐', '+')
        code = code.replace('└', '+')
        code = code.replace('┘', '+')
        code = code.replace('├', '+')
        code = code.replace('┤', '+')
        code = code.replace('┬', '+')
        code = code.replace('┴', '+')
        code = code.replace('┼', '+')
        code = code.replace('✓', '[OK]')
        code = code.replace('📱', '[Phone]')
        code = code.replace('🔍', '[Search]')
        
        lines = code.split('\n')
        for line in lines:
            if line.strip():
                self.set_x(15)
                self.multi_cell(180, 4, line, fill=True)
        self.ln(3)
        
    def table_row(self, cells, is_header=False, col_widths=None):
        if col_widths is None:
            col_widths = [190 / len(cells)] * len(cells)
        
        if is_header:
            self.set_font('Helvetica', 'B', 9)
            self.set_fill_color(52, 152, 219)
            self.set_text_color(255, 255, 255)
        else:
            self.set_font('Helvetica', '', 9)
            self.set_fill_color(245, 245, 245)
            self.set_text_color(50, 50, 50)
        
        max_height = 5
        for i, cell in enumerate(cells):
            cell = cell.replace('→', '->')
            cell = cell.replace('✓', '[OK]')
            cell = cell.replace('**', '')
            # Calculate height needed
            lines_needed = len(self.multi_cell(col_widths[i], 5, cell, split_only=True))
            max_height = max(max_height, lines_needed * 5)
        
        x_start = self.get_x()
        y_start = self.get_y()
        
        for i, cell in enumerate(cells):
            cell = cell.replace('→', '->')
            cell = cell.replace('✓', '[OK]')
            cell = cell.replace('**', '')
            self.set_xy(x_start + sum(col_widths[:i]), y_start)
            self.multi_cell(col_widths[i], 5, cell, border=1, fill=True)
        
        self.set_y(y_start + max_height)

def parse_markdown(content):
    """Parse markdown content and return structured elements"""
    elements = []
    lines = content.split('\n')
    i = 0
    in_code_block = False
    code_content = []
    in_table = False
    table_rows = []
    
    while i < len(lines):
        line = lines[i]
        
        # Code block handling
        if line.strip().startswith('```'):
            if in_code_block:
                elements.append(('code', '\n'.join(code_content)))
                code_content = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue
            
        if in_code_block:
            code_content.append(line)
            i += 1
            continue
        
        # Table handling
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            
            # Skip separator rows
            if re.match(r'^[\s|:-]+$', line):
                i += 1
                continue
                
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells:
                table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            elements.append(('table', table_rows))
            table_rows = []
            in_table = False
        
        # Headers
        if line.startswith('# '):
            elements.append(('h1', line[2:].strip()))
        elif line.startswith('## '):
            elements.append(('h2', line[3:].strip()))
        elif line.startswith('### '):
            elements.append(('h3', line[4:].strip()))
        elif line.startswith('#### '):
            elements.append(('h4', line[5:].strip()))
        # Bullet points
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            indent = len(line) - len(line.lstrip())
            text = line.strip()[2:]
            elements.append(('bullet', text, indent))
        elif re.match(r'^\d+\.\s', line.strip()):
            text = re.sub(r'^\d+\.\s', '', line.strip())
            elements.append(('bullet', text, 0))
        # Horizontal rule
        elif line.strip() in ['---', '***', '___']:
            elements.append(('hr', None))
        # Regular text
        elif line.strip():
            elements.append(('text', line.strip()))
        
        i += 1
    
    # Handle any remaining table
    if in_table and table_rows:
        elements.append(('table', table_rows))
    
    return elements

def create_pdf(md_file, output_file):
    """Create PDF from markdown file"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pdf = ConceptPaperPDF()
    pdf.set_margins(15, 20, 15)
    
    # Title Page
    pdf.add_page()
    pdf.ln(30)
    
    # University Header
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(26, 82, 118)
    pdf.cell(0, 10, 'PWANI UNIVERSITY', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, 'DEPARTMENT OF COMPUTER SCIENCE', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(20)
    
    # Title
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(26, 82, 118)
    pdf.multi_cell(0, 12, 'HEALTHLINK:\nAN INTELLIGENT AI-POWERED\nTELEMEDICINE PLATFORM', align='C')
    pdf.ln(5)
    
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(52, 152, 219)
    pdf.cell(0, 10, 'CONCEPT PAPER', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(30)
    
    # Decorative line
    pdf.set_draw_color(26, 82, 118)
    pdf.set_line_width(0.5)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(20)
    
    # Student Info
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 8, 'Submitted by:', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'ADAN HASSAN ADI', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(10)
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, 'Supervised by:', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'DR. MBOGHOLI', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(20)
    pdf.set_font('Helvetica', 'I', 12)
    pdf.cell(0, 8, 'January 2026', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Parse and render content
    elements = parse_markdown(content)
    
    for element in elements:
        elem_type = element[0]
        
        try:
            if elem_type == 'h1':
                # Skip the main title as we've already rendered it
                if 'HEALTHLINK' in element[1].upper():
                    continue
                pdf.chapter_title(element[1], 1)
            elif elem_type == 'h2':
                pdf.chapter_title(element[1], 2)
            elif elem_type == 'h3':
                pdf.chapter_title(element[1], 3)
            elif elem_type == 'h4':
                pdf.chapter_title(element[1], 4)
            elif elem_type == 'text':
                # Clean up markdown formatting
                text = element[1]
                text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # bold
                text = re.sub(r'\*(.*?)\*', r'\1', text)  # italic
                text = re.sub(r'`(.*?)`', r'\1', text)  # inline code
                pdf.body_text(text)
            elif elem_type == 'bullet':
                text = element[1]
                text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
                text = re.sub(r'\*(.*?)\*', r'\1', text)
                indent = element[2] if len(element) > 2 else 0
                pdf.bullet_point(text, indent // 2)
            elif elem_type == 'code':
                pdf.code_block(element[1])
            elif elem_type == 'table':
                table_rows = element[1]
                if table_rows:
                    # Calculate column widths based on number of columns
                    num_cols = len(table_rows[0])
                    col_widths = [180 / num_cols] * num_cols
                    
                    # First row is header
                    pdf.table_row(table_rows[0], is_header=True, col_widths=col_widths)
                    
                    # Rest are data rows
                    for row in table_rows[1:]:
                        if len(row) == num_cols:
                            pdf.table_row(row, is_header=False, col_widths=col_widths)
                    pdf.ln(3)
            elif elem_type == 'hr':
                pdf.ln(3)
                pdf.set_draw_color(200, 200, 200)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(3)
        except Exception as e:
            print(f"Warning: Could not render element: {e}")
            continue
    
    # Save PDF
    pdf.output(output_file)
    print(f"PDF created successfully: {output_file}")

if __name__ == "__main__":
    md_file = "CONCEPT_PAPER.md"
    output_file = "CONCEPT_PAPER.pdf"
    
    if os.path.exists(md_file):
        create_pdf(md_file, output_file)
    else:
        print(f"Error: {md_file} not found!")

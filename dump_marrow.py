import PyPDF2
reader = PyPDF2.PdfReader('maro/Medicine_ed8.pdf')
st = reader.pages[291].get_contents().get_data().decode('latin-1', errors='replace')
import re
for m in re.finditer(r'/(Im\d+)\s+Do', st):
    print(m.group(0))

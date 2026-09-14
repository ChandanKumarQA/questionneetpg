import PyPDF2, struct, re, time, glob, os, json, io
from PIL import Image

print("Initializing Font Engine & Image Extractor...")
with open('/System/Library/Fonts/Supplemental/Georgia.ttf', 'rb') as f:
    sys_ttf = f.read()

def parse_ttf(data):
    num_tables = struct.unpack('>H', data[4:6])[0]
    tables = {}
    for i in range(num_tables):
        tag = data[12+i*16:16+i*16].decode('latin-1')
        offset, length = struct.unpack('>II', data[20+i*16:28+i*16])
        tables[tag] = data[offset:offset+length]
    return tables

sys_tables = parse_ttf(sys_ttf)
sys_loc_fmt = struct.unpack('>h', sys_tables['head'][50:52])[0]
sys_loca, sys_glyf = sys_tables['loca'], sys_tables['glyf']
sys_num_glyphs = struct.unpack('>H', sys_tables['maxp'][4:6])[0]
sys_cmap = sys_tables['cmap']

fmt4_offset = None
for i in range(struct.unpack('>H', sys_cmap[2:4])[0]):
    p_id, e_id, offset = struct.unpack('>HHI', sys_cmap[4+i*8:12+i*8])
    if (p_id == 3 and e_id == 1) or (p_id == 0):
        fmt = struct.unpack('>H', sys_cmap[offset:offset+2])[0]
        if fmt == 4: fmt4_offset = offset; break

gid_to_char = {}
length, lang, seg_count_x2 = struct.unpack('>HHH', sys_cmap[fmt4_offset+2:fmt4_offset+8])
seg_count = seg_count_x2 // 2
end_codes = struct.unpack(f'>{seg_count}H', sys_cmap[fmt4_offset+14:fmt4_offset+14+seg_count*2])
start_codes = struct.unpack(f'>{seg_count}H', sys_cmap[fmt4_offset+16+seg_count*2:fmt4_offset+16+seg_count*4])
id_deltas = struct.unpack(f'>{seg_count}h', sys_cmap[fmt4_offset+16+seg_count*4:fmt4_offset+16+seg_count*6])
id_range_offset = fmt4_offset + 16 + seg_count * 6
for seg in range(seg_count):
    start, end, delta = start_codes[seg], end_codes[seg], id_deltas[seg]
    ro_addr = id_range_offset + seg * 2
    ro = struct.unpack('>H', sys_cmap[ro_addr:ro_addr+2])[0]
    for c in range(start, end + 1):
        if c == 0xFFFF: continue
        gid = (c + delta) & 0xFFFF if ro == 0 else struct.unpack('>H', sys_cmap[ro_addr + ro + (c - start) * 2:ro_addr + ro + (c - start) * 2 + 2])[0]
        if gid != 0 and ro != 0: gid = (gid + delta) & 0xFFFF
        if gid not in gid_to_char: gid_to_char[gid] = chr(c)

sys_header_to_char = {}
for gid in range(sys_num_glyphs):
    o1 = struct.unpack('>H' if sys_loc_fmt==0 else '>I', sys_loca[gid*(2 if sys_loc_fmt==0 else 4):gid*(2 if sys_loc_fmt==0 else 4)+(2 if sys_loc_fmt==0 else 4)])[0] * (2 if sys_loc_fmt==0 else 1)
    o2 = struct.unpack('>H' if sys_loc_fmt==0 else '>I', sys_loca[(gid+1)*(2 if sys_loc_fmt==0 else 4):(gid+1)*(2 if sys_loc_fmt==0 else 4)+(2 if sys_loc_fmt==0 else 4)])[0] * (2 if sys_loc_fmt==0 else 1)
    gdata = sys_glyf[o1:o2]
    if len(gdata) >= 10:
        hdr = gdata[:10]
        if hdr not in sys_header_to_char and gid in gid_to_char:
            sys_header_to_char[hdr] = gid_to_char[gid]

font_cache = {}

def get_font_map(font_obj):
    base = font_obj.get('/BaseFont', '')
    if base in font_cache: return font_cache[base]
    if 'Georgia' not in base: return None
    try:
        desc = font_obj['/DescendantFonts'][0].get_object()
        ttf_data = desc['/FontDescriptor'].get_object()['/FontFile2'].get_object().get_data()
        tables = parse_ttf(ttf_data)
        loc_fmt = struct.unpack('>h', tables['head'][50:52])[0]
        loca, glyf = tables['loca'], tables['glyf']
        num_g = struct.unpack('>H', tables['maxp'][4:6])[0]
        m = {}
        for egid in range(num_g):
            o1 = struct.unpack('>H' if loc_fmt==0 else '>I', loca[egid*(2 if loc_fmt==0 else 4):egid*(2 if loc_fmt==0 else 4)+(2 if loc_fmt==0 else 4)])[0] * (2 if loc_fmt==0 else 1)
            o2 = struct.unpack('>H' if loc_fmt==0 else '>I', loca[(egid+1)*(2 if loc_fmt==0 else 4):(egid+1)*(2 if loc_fmt==0 else 4)+(2 if loc_fmt==0 else 4)])[0] * (2 if loc_fmt==0 else 1)
            gdata = glyf[o1:o2]
            m[egid] = sys_header_to_char.get(gdata[:10], ' ' if len(gdata)<10 else '?')
        font_cache[base] = m
        return m
    except:
        return None

pattern = re.compile(r'(/[\w\d]+)\s+[\d\.]+\s+Tf|T\*|(?:\-?[\d\.]+)\s+(?:\-?[\d\.]+)\s+T[Dd]|\[(.*?)\]\s*TJ|\((.*?)\)\s*Tj|<([0-9A-Fa-f]+)>\s*Tj')
elem_pat = re.compile(r'<([0-9A-Fa-f]+)>|\((.*?)\)|(\-?[\d\.]+)')

def clean_escapes(text):
    text = text.replace(r'\221', "'").replace(r'\222', "'")
    text = text.replace(r'\223', '"').replace(r'\224', '"')
    text = text.replace(r'\225', '• ').replace(r'\226', '–').replace(r'\227', '—')
    text = text.replace(r'\(', '(').replace(r'\)', ')')
    text = text.replace(r'\\', '\\')
    return text

def decode_page(page):
    fonts = page.get('/Resources', {}).get('/Font', {})
    font_maps = {}
    for fk, fo in fonts.items():
        m = get_font_map(fo.get_object())
        if m: font_maps[fk] = m
    stream_bytes = page.get_contents().get_data().decode('latin-1', errors='replace')
    out = []
    cur_font = None
    for m in pattern.finditer(stream_bytes):
        font, tj_array, paren_tj, hex_tj = m.group(1), m.group(2), m.group(3), m.group(4)
        if font: cur_font = font
        elif m.group(0).startswith('T*') or 'TD' in m.group(0) or 'Td' in m.group(0): out.append('\n')
        elif hex_tj:
            gmap = font_maps.get(cur_font)
            if gmap:
                out.append(''.join(gmap.get(int(hex_tj[i:i+4], 16), '') for i in range(0, len(hex_tj), 4)))
            else:
                out.append(bytes.fromhex(hex_tj).decode('latin-1', errors='ignore'))
        elif paren_tj is not None:
            out.append(paren_tj)
        elif tj_array is not None:
            for em in elem_pat.finditer(tj_array):
                eh, ep, num = em.group(1), em.group(2), em.group(3)
                if eh:
                    gmap = font_maps.get(cur_font)
                    if gmap:
                        out.append(''.join(gmap.get(int(eh[i:i+4], 16), '') for i in range(0, len(eh), 4)))
                    else:
                        out.append(bytes.fromhex(eh).decode('latin-1', errors='ignore'))
                elif ep:
                    out.append(ep)
                elif num:
                    try:
                        if float(num) < -150:
                            out.append(' ')
                    except ValueError:
                        pass
    return clean_escapes(''.join(out))

def save_image_object(xo, out_path):
    try:
        obj = xo.get_object()
        data = obj.get_data()
        filt = obj.get('/Filter')
        w = obj.get('/Width')
        h = obj.get('/Height')
        cs_raw = obj.get('/ColorSpace')
        cs = cs_raw.get_object() if hasattr(cs_raw, 'get_object') else cs_raw

        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        # 1. JPEG
        if filt == '/DCTDecode' or (isinstance(filt, (list, tuple)) and '/DCTDecode' in filt) or data.startswith(b'\xff\xd8\xff'):
            im = Image.open(io.BytesIO(data))
            if im.mode == 'CMYK':
                im = im.convert('RGB')
            im.save(out_path, 'JPEG', quality=90)
            return True

        # 2. FlateDecode or Raw bytes
        if w and h:
            # Indexed Color Space
            if isinstance(cs, list) and len(cs) >= 4 and cs[0] == '/Indexed':
                pal_raw = cs[3].get_object() if hasattr(cs[3], 'get_object') else cs[3]
                pal_data = pal_raw.get_data() if hasattr(pal_raw, 'get_data') else bytes(pal_raw)
                im = Image.frombytes('P', (w, h), data)
                im.putpalette(pal_data)
                im = im.convert('RGB')
                im.save(out_path, 'JPEG', quality=90)
                return True
            
            # RGB
            if len(data) == w * h * 3:
                im = Image.frombytes('RGB', (w, h), data)
                im.save(out_path, 'JPEG', quality=90)
                return True
                
            # Grayscale
            if len(data) == w * h:
                im = Image.frombytes('L', (w, h), data)
                im = im.convert('RGB')
                im.save(out_path, 'JPEG', quality=90)
                return True

            # CMYK
            if len(data) == w * h * 4:
                im = Image.frombytes('CMYK', (w, h), data)
                im = im.convert('RGB')
                im.save(out_path, 'JPEG', quality=90)
                return True

        # Fallback to PIL Image.open
        im = Image.open(io.BytesIO(data))
        if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
            bg = Image.new('RGB', im.size, (255, 255, 255))
            bg.paste(im, (0, 0), im.convert('RGBA'))
            im = bg
        elif im.mode != 'RGB':
            im = im.convert('RGB')
        im.save(out_path, 'JPEG', quality=90)
        return True
    except Exception:
        return False

def extract_subject(pdf_file):
    t_start = time.time()
    subj_name = os.path.basename(pdf_file).replace('_ed8.pdf', '').replace('_', ' ')
    subj_slug = subj_name.lower().replace(' ', '_')
    reader = PyPDF2.PdfReader(pdf_file)
    total_pages = len(reader.pages)
    
    # TOC
    toc_text = ''
    for p in range(1, min(5, total_pages)):
        t = reader.pages[p].extract_text()
        if t: toc_text += t + '\n'
    chapters = []
    for line in toc_text.split('\n'):
        m = re.search(r'^(\d+)\s+(.*?)\s+(\d+)$', line.strip())
        if m: chapters.append((int(m.group(1)), m.group(2).strip(), int(m.group(3))))
    if not chapters: chapters = [(1, subj_name, 1)]
    
    all_mcqs = []
    total_q_imgs = 0
    total_sol_imgs = 0
    
    token_pat = re.compile(r'/(Im\d+)\s+Do|(Question\s+\d+\s*:)|(Solution\s+to\s+Question\s*\d+\s*:)|(Answer\s+Key)')
    
    for idx, (ch_num, ch_title, start_pg) in enumerate(chapters):
        end_pg = chapters[idx+1][2] if idx + 1 < len(chapters) else total_pages + 1
        
        ch_text = ''
        q_imgs_map = {}   # q_num -> [xo_objs]
        sol_imgs_map = {} # sol_q_num -> [xo_objs]
        
        in_sol = False
        cur_q = None
        cur_sol = None
        
        for p in range(start_pg - 1, min(end_pg - 1, total_pages)):
            page = reader.pages[p]
            ch_text += decode_page(page) + '\n---PAGE---\n'
            
            # Map images in order
            st = page.get_contents().get_data().decode('latin-1', errors='replace')
            xobjs = page.get('/Resources', {}).get('/XObject', {})
            
            for m in token_pat.finditer(st):
                img, q_hdr, sol_hdr, ak = m.group(1), m.group(2), m.group(3), m.group(4)
                if ak:
                    in_sol = True
                    cur_q = None
                elif q_hdr and not in_sol:
                    cur_q = int(re.search(r'\d+', q_hdr).group(0))
                elif sol_hdr:
                    in_sol = True
                    cur_sol = int(re.search(r'\d+', sol_hdr).group(0))
                elif img:
                    xo = xobjs.get(f'/{img}')
                    if xo:
                        if not in_sol and cur_q is not None:
                            q_imgs_map.setdefault(cur_q, []).append((img, xo))
                        elif in_sol and cur_sol is not None:
                            sol_imgs_map.setdefault(cur_sol, []).append((img, xo))
        
        # 1. Answer Key
        ans_key = {}
        ans_match = re.search(r'Answer\s+Key.*?Question\s+No\.\s*Correct\s+Option\s*([\s\S]*?)(?:Detailed\s+Explanations|$)', ch_text, re.I)
        if ans_match:
            for qn, ans in re.findall(r'(\d+)\s+([a-d])', ans_match.group(1), re.I):
                ans_key[int(qn)] = ans.lower()
        
        # 2. Solutions
        sols = {}
        sol_matches = re.finditer(r'Solution\s+to\s+Question\s*(\d+)\s*:\s*([\s\S]*?)(?=(?:Solution\s+to\s+Question|\Z))', ch_text, re.I)
        for sm in sol_matches:
            qn = int(sm.group(1))
            stext = sm.group(2).replace('Sold by @itachibot', '').replace('---PAGE---', '')
            stext = re.sub(r'\n\s*\d+\s*\n', '\n', stext)
            stext = re.sub(r'/[0-9]+$', '', stext.strip())
            sols[qn] = '\n'.join([line.strip() for line in stext.split('\n') if line.strip()])

        
        # 3. Questions
        q_part = ch_text.split('Answer Key')[0]
        q_part = q_part.replace('Sold by @itachibot', '')
        q_part = re.sub(r'(\d+)\s*\n---PAGE---', '\n---PAGE---', q_part)
        q_splits = re.split(r'(Question\s+\d+\s*:)', q_part)
        
        for i in range(1, len(q_splits), 2):
            q_hdr = q_splits[i]
            q_body = q_splits[i+1]
            qn = int(re.search(r'\d+', q_hdr).group(0))
            
            opt_splits = re.split(r'([a-dA-D]\))', q_body)
            q_text = re.sub(r'---PAGE---|\d+$', '', opt_splits[0]).strip()
            q_text = '\n'.join([line.strip() for line in q_text.split('\n') if line.strip()])

            
            opts = {}
            if len(opt_splits) > 1:
                for j in range(1, len(opt_splits), 2):
                    let = opt_splits[j][0].lower()
                    val = opt_splits[j+1] if j+1 < len(opt_splits) else ''
                    val = re.sub(r'---PAGE---|\d+$', '', val).strip()
                    opts[let] = '\n'.join([line.strip() for line in val.split('\n') if line.strip()])

            
            if len(opts) >= 2 and len(q_text) > 10:
                # Save question images if any
                saved_q_imgs = []
                if qn in q_imgs_map:
                    for im_idx, (img_tag, xo) in enumerate(q_imgs_map[qn]):
                        filename = f"images/{subj_slug}/ch{ch_num}_q{qn}_{im_idx+1}.jpg" if len(q_imgs_map[qn]) > 1 else f"images/{subj_slug}/ch{ch_num}_q{qn}.jpg"
                        if save_image_object(xo, filename):
                            saved_q_imgs.append(filename)
                            total_q_imgs += 1
                
                # Save solution images if any
                saved_sol_imgs = []
                if qn in sol_imgs_map:
                    for im_idx, (img_tag, xo) in enumerate(sol_imgs_map[qn]):
                        filename = f"images/{subj_slug}/ch{ch_num}_q{qn}_sol_{im_idx+1}.jpg" if len(sol_imgs_map[qn]) > 1 else f"images/{subj_slug}/ch{ch_num}_q{qn}_sol.jpg"
                        if save_image_object(xo, filename):
                            saved_sol_imgs.append(filename)
                            total_sol_imgs += 1
                
                mcq_obj = {
                    'id': f"{subj_name[:3].upper()}-CH{ch_num}-Q{qn}",
                    'subject': subj_name,
                    'chapter_num': ch_num,
                    'chapter': ch_title,
                    'q_num': qn,
                    'question': q_text,
                    'options': opts,
                    'answer': ans_key.get(qn, ''),
                    'explanation': sols.get(qn, '')
                }
                mcq_obj['images'] = saved_q_imgs
                mcq_obj['solution_images'] = saved_sol_imgs
                
                all_mcqs.append(mcq_obj)
                
    elapsed = time.time() - t_start
    print(f"✓ {subj_name}: {len(all_mcqs)} MCQs ({total_q_imgs} Q-images, {total_sol_imgs} Sol-images) in {elapsed:.1f}s")
    return subj_name, chapters, all_mcqs

if __name__ == '__main__':
    pdf_files = sorted(glob.glob('maro/*_ed8.pdf') or glob.glob('*_ed8.pdf'))
    if not pdf_files:
        print("No _ed8.pdf files found in maro/ or current directory!")
    all_data = {}
    total_extracted_mcqs = 0
    total_all_q_imgs = 0
    total_all_sol_imgs = 0

    for pdf in pdf_files:
        subj, chs, mcqs = extract_subject(pdf)
        total_extracted_mcqs += len(mcqs)
        q_imgs_count = sum(len(m.get('images', [])) for m in mcqs)
        sol_imgs_count = sum(len(m.get('solution_images', [])) for m in mcqs)
        total_all_q_imgs += q_imgs_count
        total_all_sol_imgs += sol_imgs_count
        
        all_data[subj] = {
            'total_extracted': len(mcqs),
            'chapters_count': len(chs),
            'chapters': [{'num': c[0], 'title': c[1], 'page': c[2]} for c in chs],
            'question_images_count': q_imgs_count,
            'solution_images_count': sol_imgs_count,
            'mcqs': mcqs
        }

    print(f"\n==========================================")
    print(f"Total Subjects: {len(all_data)}")
    print(f"Total MCQs Extracted: {total_extracted_mcqs}")
    print(f"Total Question Images Saved: {total_all_q_imgs}")
    print(f"Total Solution Images Saved: {total_all_sol_imgs}")
    print(f"==========================================")

    # Save full mcq_data.json
    with open('mcq_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"Saved mcq_data.json ({os.path.getsize('mcq_data.json')} bytes)")

    # Curated set: ensure inclusion of image-based questions!
    curated = {}
    for subj, info in all_data.items():
        mcqs = info['mcqs']
        # Filter with valid answers & explanations
        with_ans = [q for q in mcqs if q['answer'] and q['explanation']]
        
        # Priority: ensure image-based questions are in curated!
        ibq_questions = [q for q in with_ans if 'images' in q]
        non_ibq = [q for q in with_ans if 'images' not in q]
        
        # Select up to 15 IBQ questions + 35 diverse non-IBQ questions
        selected_ibq = ibq_questions[:15]
        remaining_needed = 50 - len(selected_ibq)
        
        step = max(1, len(non_ibq) // remaining_needed) if remaining_needed > 0 and len(non_ibq) > remaining_needed else 1
        selected_non_ibq = non_ibq[::step][:remaining_needed]
        
        combined = selected_ibq + selected_non_ibq
        curated[subj] = {
            'total': len(mcqs),
            'selected_count': len(combined),
            'ibq_count': len([q for q in combined if 'images' in q]),
            'mcqs': combined
        }

    with open('mcq_curated.json', 'w', encoding='utf-8') as f:
        json.dump(curated, f, ensure_ascii=False, indent=2)

    print(f"Saved mcq_curated.json ({os.path.getsize('mcq_curated.json')} bytes)")


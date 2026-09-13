import os, sys, glob, re, json, time
import PyPDF2
from PIL import Image

PDF_MAP = {
    'Anaesthesia Prepladder Version X Qbank.pdf': 'Anaesthesia',
    'Anatomy Prepladder Version X Qbank.pdf': 'Anatomy',
    'Watermarked_Biochemistry_Prepladder.pdf': 'Biochemistry',
    'Watermarked_Dermatology_Prepladder.pdf': 'Dermatology',
    'ENT Prepladder Version X Qbank.pdf': 'ENT',
    'Watermarked_Forensic_Medicine_Prepladder.pdf': 'Forensic Medicine',
    'Watermarked_Gynaecology_Obstetrics_Prepladder.pdf': 'OBGYN',
    'Watermarked_Medicine_Prepladder.pdf': 'Medicine',
    'Watermarked_Microbiology_Prepladder.pdf': 'Microbiology',
    'Watermarked_Ophthalmology_Prepladder.pdf': 'Ophthalmology',
    'Watermarked_Orthopaedics_Prepladder.pdf': 'Orthopaedics',
    'Watermarked_Pathology_Prepladder.pdf': 'Pathology',
    'Watermarked_Pediatrics_Prepladder.pdf': 'Pediatrics',
    'Pharmacology Prepladder Version X Qbank.pdf': 'Pharmacology',
    'Physiology Prepladder Version X Qbank.pdf': 'Physiology',
    'Watermarked_PSM_Prepladder.pdf': 'PSM',
    'Watermarked_Psychiatry_Prepladder.pdf': 'Psychiatry',
    'Watermarked_Radiology_Prepladder.pdf': 'Radiology',
    'Watermarked_Surgery_Prepladder.pdf': 'Surgery'
}

SUBJECT_META = {
    "Anaesthesia": {"icon": "💉", "color": "#06b6d4"},
    "Anatomy": {"icon": "🦷", "color": "#7c3aed"},
    "Biochemistry": {"icon": "🧬", "color": "#8b5cf6"},
    "Dermatology": {"icon": "🩹", "color": "#f472b6"},
    "ENT": {"icon": "👂", "color": "#ec4899"},
    "Forensic Medicine": {"icon": "⚖️", "color": "#f59e0b"},
    "Medicine": {"icon": "🩺", "color": "#0ea5e9"},
    "Microbiology": {"icon": "🦠", "color": "#22c55e"},
    "OBGYN": {"icon": "🤰", "color": "#e879f9"},
    "Ophthalmology": {"icon": "👁️", "color": "#10b981"},
    "Orthopaedics": {"icon": "🦴", "color": "#3b82f6"},
    "PSM": {"icon": "🏥", "color": "#14b8a6"},
    "Pathology": {"icon": "🔬", "color": "#ef4444"},
    "Pediatrics": {"icon": "👶", "color": "#fbbf24"},
    "Pharmacology": {"icon": "💊", "color": "#f43f5e"},
    "Physiology": {"icon": "🫀", "color": "#eab308"},
    "Psychiatry": {"icon": "🧠", "color": "#a855f7"},
    "Radiology": {"icon": "📡", "color": "#38bdf8"},
    "Surgery": {"icon": "🔪", "color": "#fb923c"}
}

IBQ_KEYWORDS = [
    "image", "given below", "shown", "arrow", "marked", "labeled", 
    "labelled", "diagram", "identify", "depicted", "picture", "scan", 
    "radiograph", "x-ray", "ct", "figure", "mri", "histology", "finding",
    "photograph", "specimen", "ecg", "chart"
]

def clean_watermarks(t):
    if not t: return ""
    # Strip Telegram & Prepladder watermarks
    t = re.sub(r'Prepladder\s+X\s+Qbank[^\n]*', '', t, flags=re.I)
    t = re.sub(r'Search\s+On\s+Tg\s*[:-][^\n]*', '', t, flags=re.I)
    t = re.sub(r'https?://t\.me/[^\s\n]+', '', t, flags=re.I)
    t = re.sub(r't\.me/[^\s\n]+', '', t, flags=re.I)
    t = re.sub(r'@\w*fckk\w*', '', t, flags=re.I)
    t = re.sub(r'@itachibot[^\n]*', '', t, flags=re.I)
    t = re.sub(r'Sold\s+by\s+@\w+', '', t, flags=re.I)
    t = re.sub(r'Page\s+\d+\s+of\s+\d+', '', t, flags=re.I)
    t = re.sub(r'\{\{caption_text\}\}', '', t)
    t = t.replace('\x7f', ' ')
    return " ".join(t.split())

def parse_toc(reader):
    toc_lines = []
    max_search = min(25, len(reader.pages))
    for p in range(1, max_search):
        txt = reader.pages[p].extract_text() or ""
        found_on_page = 0
        for line in txt.split('\n'):
            line = line.strip()
            m = re.match(r'^(\d+)\.\s*(.*?)\s+(\d+)$', line)
            if m:
                ch_num = int(m.group(1))
                ch_title = m.group(2).strip()
                page_num = int(m.group(3))
                toc_lines.append((ch_num, ch_title, page_num))
                found_on_page += 1
        if toc_lines and found_on_page == 0 and p >= toc_lines[0][2] - 1:
            break
            
    unique = {}
    for num, title, page in toc_lines:
        if num not in unique:
            unique[num] = (num, title, page)
            
    sorted_toc = [unique[k] for k in sorted(unique.keys())]
    
    enriched = []
    last_topic = "General"
    for num, title, page in sorted_toc:
        if "Previous Year" in title:
            clean_title = f"PYQs - {last_topic}"
        else:
            clean_title = title
            last_topic = title
        enriched.append((num, clean_title, page))
        
    return enriched

def save_image_file(img_obj, out_path):
    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        data = img_obj.data if hasattr(img_obj, 'data') else img_obj
        with open(out_path, 'wb') as f:
            f.write(data)
        try:
            im = Image.open(out_path)
            if im.mode == 'CMYK':
                im = im.convert('RGB')
                im.save(out_path, 'JPEG', quality=85)
        except Exception:
            pass
        return True
    except Exception:
        return False

def extract_subject_mcqs(pdf_path, subject_name):
    print(f"\nProcessing {subject_name} ({os.path.basename(pdf_path)})...")
    t0 = time.time()
    
    reader = PyPDF2.PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"  Total pages: {total_pages}")
    
    toc = parse_toc(reader)
    print(f"  Parsed {len(toc)} chapters from TOC")
    if not toc:
        print(f"  WARNING: No TOC found for {subject_name}")
        return []
        
    subj_slug = subject_name.lower().replace(" ", "_").replace("&", "")
    img_dir = f"images/prep/{subj_slug}"
    os.makedirs(img_dir, exist_ok=True)
    
    # Pre-extract all images page by page
    page_images_raw = {}
    for p_idx in range(total_pages):
        page = reader.pages[p_idx]
        if hasattr(page, 'images') and len(page.images) > 0:
            page_images_raw[p_idx + 1] = list(page.images)
            
    subject_mcqs = []
    total_q_imgs_saved = 0
    total_sol_imgs_saved = 0
    
    for i, (ch_num, ch_title, start_page) in enumerate(toc):
        end_page = toc[i+1][2] - 1 if i+1 < len(toc) else total_pages
        if end_page < start_page:
            end_page = start_page
            
        chapter_pages = []
        for p_num in range(start_page, end_page + 1):
            if p_num <= total_pages:
                txt = reader.pages[p_num - 1].extract_text() or ""
                chapter_pages.append((p_num, txt))
                
        # Find where solutions start
        sol_start_page = end_page + 1
        for p_num, p_txt in chapter_pages:
            if 'Correct Answers' in p_txt or 'Solution for Question 1:' in p_txt:
                sol_start_page = p_num
                break
                
        # 1. Parse Solutions & Solution Images
        solutions_dict = {}
        sol_imgs_map = {} # q_num -> [img_paths]
        
        # Track cur_sol across solution pages
        cur_sol = None
        for p_num in range(sol_start_page, end_page + 1):
            if p_num > total_pages: continue
            txt = reader.pages[p_num - 1].extract_text() or ""
            sol_matches = list(re.finditer(r'Solution for Question\s+(\d+):', txt))
            
            p_imgs = page_images_raw.get(p_num, [])
            if sol_matches:
                # If there are solution headers on this page
                cur_sol = int(sol_matches[0].group(1))
                if p_imgs:
                    for im_idx, img_obj in enumerate(p_imgs):
                        # Determine which sol header it is closest to
                        target_sol = int(sol_matches[-1].group(1)) if len(sol_matches) > 1 and im_idx > 0 else cur_sol
                        img_filename = f"images/prep/{subj_slug}/ch{ch_num}_q{target_sol}_sol_{im_idx+1}.jpg" if len(p_imgs) > 1 else f"images/prep/{subj_slug}/ch{ch_num}_q{target_sol}_sol.jpg"
                        if save_image_file(img_obj, img_filename):
                            sol_imgs_map.setdefault(target_sol, []).append(img_filename)
                            total_sol_imgs_saved += 1
                cur_sol = int(sol_matches[-1].group(1))
            else:
                # Continuation page of previous solution
                if cur_sol is not None and p_imgs:
                    for im_idx, img_obj in enumerate(p_imgs):
                        img_filename = f"images/prep/{subj_slug}/ch{ch_num}_q{cur_sol}_sol_c{im_idx+1}.jpg"
                        if save_image_file(img_obj, img_filename):
                            sol_imgs_map.setdefault(cur_sol, []).append(img_filename)
                            total_sol_imgs_saved += 1
                            
        # Parse solution text
        full_ch_text = "\n".join([t[1] for t in chapter_pages])
        ca_pos = full_ch_text.find('Correct Answers')
        if ca_pos == -1: ca_pos = full_ch_text.find('Solution for Question 1:')
        if ca_pos == -1: ca_pos = full_ch_text.find('Correct Answer:')
        
        q_block = full_ch_text[:ca_pos].strip() if ca_pos != -1 else full_ch_text.strip()
        s_block = full_ch_text[ca_pos:].strip() if ca_pos != -1 else ""
        
        ans_table = {}
        for qn, a in re.findall(r'Question\s+(\d+)\s+([1-4A-D])', s_block):
            ans_table[int(qn)] = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}.get(a, a)
            
        sol_splits = re.split(r'Solution for Question\s+(\d+):', s_block)
        if len(sol_splits) > 1:
            for s_i in range(1, len(sol_splits), 2):
                q_idx = int(sol_splits[s_i])
                sol_body = sol_splits[s_i + 1]
                
                ans_letter = None
                ca_match = re.search(r'Correct Answer:\s*([A-D])\)?', sol_body)
                if ca_match:
                    ans_letter = ca_match.group(1)
                elif q_idx in ans_table:
                    ans_letter = ans_table[q_idx]
                    
                exp_text = ""
                exp_match = re.search(r'Explanation\s*[:\n]\s*(.*?)(?=\n(?:Correct Answer|Solution for Question|\Z))', sol_body, re.DOTALL)
                if exp_match:
                    exp_text = clean_watermarks(exp_match.group(1))
                else:
                    exp_text = clean_watermarks(sol_body[:1500])
                    
                solutions_dict[q_idx] = {
                    "answer": ans_letter or "A",
                    "explanation": exp_text
                }
                
        # 2. Map Question Images on Question Pages
        q_imgs_map = {} # q_num -> [img_paths]
        q_on_pages = {} # q_num -> page_num
        for p_num in range(start_page, min(sol_start_page, total_pages + 1)):
            txt = reader.pages[p_num - 1].extract_text() or ""
            p_imgs = page_images_raw.get(p_num, [])
            
            # Find questions on this page
            page_q_chunks = list(re.finditer(r'(?:^|\n)(\d+)\.\s+(.*?)(?=\n\d+\.|\Z)', txt, re.DOTALL))
            kw_cands = []
            all_cands = []
            for qm in page_q_chunks:
                qn = int(qm.group(1))
                q_on_pages[qn] = p_num
                all_cands.append(qn)
                q_snippet = qm.group(2).lower()
                if any(k in q_snippet for k in IBQ_KEYWORDS):
                    kw_cands.append(qn)
                    
            if p_imgs:
                # If question specifically asks for an image on this page
                if kw_cands:
                    target_q = kw_cands[0]
                    for im_idx, img_obj in enumerate(p_imgs):
                        img_filename = f"images/prep/{subj_slug}/ch{ch_num}_q{target_q}_{im_idx+1}.jpg" if len(p_imgs) > 1 else f"images/prep/{subj_slug}/ch{ch_num}_q{target_q}.jpg"
                        if save_image_file(img_obj, img_filename):
                            q_imgs_map.setdefault(target_q, []).append(img_filename)
                            total_q_imgs_saved += 1
                elif len(all_cands) == 1:
                    target_q = all_cands[0]
                    for im_idx, img_obj in enumerate(p_imgs):
                        img_filename = f"images/prep/{subj_slug}/ch{ch_num}_q{target_q}_{im_idx+1}.jpg" if len(p_imgs) > 1 else f"images/prep/{subj_slug}/ch{ch_num}_q{target_q}.jpg"
                        if save_image_file(img_obj, img_filename):
                            q_imgs_map.setdefault(target_q, []).append(img_filename)
                            total_q_imgs_saved += 1
                            
        # 3. Parse Question Body & Options
        q_chunks = re.split(r'\n(?=\d+\.\s+)', '\n' + q_block)
        for chunk in q_chunks[1:]:
            chunk = chunk.strip()
            if not chunk: continue
            
            m = re.match(r'^(\d+)\.\s*(.*?)(?=\n[A-D]\.|\Z)', chunk, re.DOTALL)
            if not m: continue
            
            q_num = int(m.group(1))
            q_text = clean_watermarks(m.group(2))
            
            # Options
            options = {}
            opt_matches = list(re.finditer(r'\n([A-D])\.\s*(.*?)(?=\n[A-D]\.|\Z)', chunk, re.DOTALL))
            for om in opt_matches:
                letter = om.group(1)
                opt_text = clean_watermarks(om.group(2))
                options[letter] = opt_text
                
            # Fallback for inline or image-based options
            sol_info = solutions_dict.get(q_num, {})
            exp = sol_info.get("explanation", "")
            
            # If options are fewer than 4, check inline format or recover from explanation
            if len(options) < 4:
                # Check inline format: A. ... B. ... C. ... D. ...
                inline_m = re.search(r'(?:^|\n)A\.\s*(.*?)\s+B\.\s*(.*?)\s+C\.\s*(.*?)\s+D\.\s*(.*)', chunk)
                if inline_m:
                    options['A'] = clean_watermarks(inline_m.group(1))
                    options['B'] = clean_watermarks(inline_m.group(2))
                    options['C'] = clean_watermarks(inline_m.group(3))
                    options['D'] = clean_watermarks(inline_m.group(4))
                else:
                    # Recover option descriptions from explanation or assign clean labels
                    for let in ['A', 'B', 'C', 'D']:
                        if let not in options or not options[let] or options[let].strip() in ['B.', 'C.', 'D.', '']:
                            # Try to extract Option X from explanation
                            exp_opt = re.search(rf'Option\s+{let}\s*[:\-\)]\s*([^\.\n]+)', exp, re.I)
                            if exp_opt and len(exp_opt.group(1).strip()) > 3:
                                options[let] = clean_watermarks(exp_opt.group(1))
                            else:
                                options[let] = f"Option {let}"
                                
            # Ensure all 4 options exist
            for let in ['A', 'B', 'C', 'D']:
                if let not in options or not options[let]:
                    options[let] = f"Option {let}"
                    
            correct_ans = sol_info.get("answer") or ans_table.get(q_num, "A")
            
            mcq_obj = {
                "id": f"prep_{subj_slug}_{ch_num}_{q_num}",
                "subject": subject_name,
                "chapter": ch_title,
                "chapter_num": ch_num,
                "q_num": q_num,
                "question": q_text,
                "options": options,
                "answer": correct_ans,
                "explanation": exp,
                "images": q_imgs_map.get(q_num, []),
                "solution_images": sol_imgs_map.get(q_num, [])
            }
            subject_mcqs.append(mcq_obj)
            
    dt = time.time() - t0
    ibq_count = sum(1 for q in subject_mcqs if q.get('images'))
    sol_img_count = sum(1 for q in subject_mcqs if q.get('solution_images'))
    print(f"  Extracted {len(subject_mcqs)} MCQs ({ibq_count} IBQs, {sol_img_count} Sol-Imgs) for {subject_name} in {dt:.1f}s")
    return subject_mcqs

def main():
    print("=" * 60)
    print("PREPLADDER VERSION X FULL EXTRACTION PIPELINE")
    print("=" * 60)
    
    total_start = time.time()
    all_prep_data = {}
    total_mcqs = 0
    total_ibqs = 0
    total_sol_imgs = 0
    
    for pdf_filename, subj_name in PDF_MAP.items():
        pdf_path = os.path.join("prep", pdf_filename)
        if not os.path.exists(pdf_path):
            print(f"File missing: {pdf_path}")
            continue
            
        mcqs = extract_subject_mcqs(pdf_path, subj_name)
        meta = SUBJECT_META.get(subj_name, {"icon": "📚", "color": "#3b82f6"})
        
        all_prep_data[subj_name] = {
            "icon": meta["icon"],
            "color": meta["color"],
            "total": len(mcqs),
            "mcqs": mcqs
        }
        
        subj_ibqs = sum(1 for q in mcqs if q.get('images'))
        subj_sol_imgs = sum(1 for q in mcqs if q.get('solution_images'))
        total_mcqs += len(mcqs)
        total_ibqs += subj_ibqs
        total_sol_imgs += subj_sol_imgs
        
    print("\n" + "=" * 60)
    print(f"EXTRACTION COMPLETE: {total_mcqs} MCQs ({total_ibqs} IBQs, {total_sol_imgs} Sol-Imgs) across {len(all_prep_data)} subjects")
    print(f"Total time: {time.time() - total_start:.1f}s")
    print("=" * 60)
    
    output_path = "prep_mcq_data.json"
    print(f"Saving to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_prep_data, f, ensure_ascii=False)
        
    print(f"File size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    main()

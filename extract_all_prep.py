import os, sys, glob, re, json, time
import PyPDF2

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

def clean_text(t):
    if not t: return ""
    return " ".join(t.split())

def parse_toc(reader):
    toc_lines = []
    # Search first 25 pages for TOC entries
    max_search = min(25, len(reader.pages))
    for p in range(1, max_search):
        txt = reader.pages[p].extract_text() or ""
        found_on_page = 0
        for line in txt.split('\n'):
            line = line.strip()
            # matches '1.Introduction and PAC 4' or '1. Introduction 4'
            m = re.match(r'^(\d+)\.\s*(.*?)\s+(\d+)$', line)
            if m:
                ch_num = int(m.group(1))
                ch_title = m.group(2).strip()
                page_num = int(m.group(3))
                toc_lines.append((ch_num, ch_title, page_num))
                found_on_page += 1
        if toc_lines and found_on_page == 0 and p >= toc_lines[0][2] - 1:
            break
            
    # Deduplicate and sort by chapter number
    unique = {}
    for num, title, page in toc_lines:
        if num not in unique:
            unique[num] = (num, title, page)
            
    sorted_toc = [unique[k] for k in sorted(unique.keys())]
    
    # Enrich "Previous Year Questions" titles
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
    
    # Pre-extract images per page
    page_images = {}
    for p_idx in range(total_pages):
        page = reader.pages[p_idx]
        if hasattr(page, 'images') and len(page.images) > 0:
            p_num = p_idx + 1
            imgs_on_page = []
            for img_idx, img in enumerate(page.images):
                img_name = f"p{p_num}_{img_idx}.jpg"
                img_path = os.path.join(img_dir, img_name)
                rel_path = f"images/prep/{subj_slug}/{img_name}"
                if not os.path.exists(img_path):
                    try:
                        with open(img_path, 'wb') as f:
                            f.write(img.data)
                    except Exception:
                        pass
                imgs_on_page.append(rel_path)
            if imgs_on_page:
                page_images[p_num] = imgs_on_page

    subject_mcqs = []
    
    for i, (ch_num, ch_title, start_page) in enumerate(toc):
        end_page = toc[i+1][2] - 1 if i+1 < len(toc) else total_pages
        if end_page < start_page:
            end_page = start_page
            
        # Extract text page by page to track question-page mapping
        chapter_pages = []
        for p_num in range(start_page, end_page + 1):
            if p_num <= total_pages:
                txt = reader.pages[p_num - 1].extract_text() or ""
                # Remove header/footer noise
                txt = re.sub(r'Prepladder X Qbank\s+.*?Page \d+ of \d+', '', txt)
                chapter_pages.append((p_num, txt))
                
        full_ch_text = "\n".join([t[1] for t in chapter_pages])
        
        # Locate answers and solutions section
        ca_pos = full_ch_text.find('Correct Answers')
        if ca_pos == -1:
            ca_pos = full_ch_text.find('Solution for Question 1:')
        if ca_pos == -1:
            ca_pos = full_ch_text.find('Correct Answer:')
            
        q_block = full_ch_text[:ca_pos].strip() if ca_pos != -1 else full_ch_text.strip()
        s_block = full_ch_text[ca_pos:].strip() if ca_pos != -1 else ""
        
        # Parse Answer Keys from table if available
        ans_table = {}
        table_matches = re.findall(r'Question\s+(\d+)\s+([1-4A-D])', s_block)
        num_to_let = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
        for qn, a in table_matches:
            ans_table[int(qn)] = num_to_let.get(a, a)
            
        # Parse individual Solutions: Solution for Question X
        solutions_dict = {}
        sol_splits = re.split(r'Solution for Question\s+(\d+):', s_block)
        if len(sol_splits) > 1:
            for s_i in range(1, len(sol_splits), 2):
                q_idx = int(sol_splits[s_i])
                sol_body = sol_splits[s_i + 1]
                
                # Correct Answer
                ans_letter = None
                ca_match = re.search(r'Correct Answer:\s*([A-D])\)?', sol_body)
                if ca_match:
                    ans_letter = ca_match.group(1)
                elif q_idx in ans_table:
                    ans_letter = ans_table[q_idx]
                    
                # Explanation
                exp_text = ""
                exp_match = re.search(r'Explanation\s*[:\n]\s*(.*?)(?=\n(?:Correct Answer|Solution for Question|\Z))', sol_body, re.DOTALL)
                if exp_match:
                    exp_text = clean_text(exp_match.group(1))
                else:
                    exp_text = clean_text(sol_body[:1200])
                    
                solutions_dict[q_idx] = {
                    "answer": ans_letter or "A",
                    "explanation": exp_text
                }
                
        # Parse Questions
        q_chunks = re.split(r'\n(?=\d+\.\s+)', '\n' + q_block)
        
        # Collect question images in question pages
        sol_start_page = start_page
        for p_num, p_txt in chapter_pages:
            if 'Correct Answers' in p_txt or 'Solution for Question 1:' in p_txt:
                sol_start_page = p_num
                break
        else:
            sol_start_page = end_page
            
        q_page_images = []
        for p_num in range(start_page, sol_start_page + 1):
            if p_num in page_images:
                q_page_images.extend(page_images[p_num])
                
        for chunk in q_chunks[1:]:
            chunk = chunk.strip()
            if not chunk: continue
            
            # Question number and text
            m = re.match(r'^(\d+)\.\s*(.*?)(?=\n[A-D]\.|\Z)', chunk, re.DOTALL)
            if not m: continue
            
            q_num = int(m.group(1))
            q_text = clean_text(m.group(2))
            
            # Options
            options = {}
            opt_matches = list(re.finditer(r'\n([A-D])\.\s*(.*?)(?=\n[A-D]\.|\Z)', chunk, re.DOTALL))
            for om in opt_matches:
                letter = om.group(1)
                opt_text = clean_text(om.group(2))
                options[letter] = opt_text
                
            if len(options) < 2:
                continue
                
            # Answers & Explanation
            sol_info = solutions_dict.get(q_num, {})
            correct_ans = sol_info.get("answer") or ans_table.get(q_num, "A")
            explanation = sol_info.get("explanation", "")
            
            # Associate images if question text references 'image' or 'figure' or if image on page
            q_imgs = []
            if "image" in q_text.lower() or "given below" in q_text.lower() or "shown" in q_text.lower():
                if q_page_images:
                    q_imgs = [q_page_images[0]]
            
            mcq_obj = {
                "id": f"prep_{subj_slug}_{ch_num}_{q_num}",
                "subject": subject_name,
                "chapter": ch_title,
                "chapter_num": ch_num,
                "q_num": q_num,
                "question": q_text,
                "options": options,
                "answer": correct_ans,
                "explanation": explanation,
                "images": q_imgs,
                "solution_images": []
            }
            subject_mcqs.append(mcq_obj)
            
    dt = time.time() - t0
    ibq_count = sum(1 for q in subject_mcqs if q.get('images'))
    print(f"  Extracted {len(subject_mcqs)} MCQs ({ibq_count} IBQs) for {subject_name} in {dt:.1f}s")
    return subject_mcqs

def main():
    print("=" * 60)
    print("PREPLADDER VERSION X FULL EXTRACTION PIPELINE")
    print("=" * 60)
    
    total_start = time.time()
    all_prep_data = {}
    total_mcqs = 0
    total_ibqs = 0
    
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
        total_mcqs += len(mcqs)
        total_ibqs += subj_ibqs
        
    print("\n" + "=" * 60)
    print(f"EXTRACTION COMPLETE: {total_mcqs} MCQs ({total_ibqs} IBQs) across {len(all_prep_data)} subjects")
    print(f"Total time: {time.time() - total_start:.1f}s")
    print("=" * 60)
    
    output_path = "prep_mcq_data.json"
    print(f"Saving to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_prep_data, f, ensure_ascii=False)
        
    print(f"File size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    main()

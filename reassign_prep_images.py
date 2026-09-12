import os, sys, re, json, time
import PyPDF2

PDF_MAP = {
    'Anaesthesia': 'Anaesthesia Prepladder Version X Qbank.pdf',
    'Anatomy': 'Anatomy Prepladder Version X Qbank.pdf',
    'Biochemistry': 'Watermarked_Biochemistry_Prepladder.pdf',
    'Dermatology': 'Watermarked_Dermatology_Prepladder.pdf',
    'ENT': 'ENT Prepladder Version X Qbank.pdf',
    'Forensic Medicine': 'Watermarked_Forensic_Medicine_Prepladder.pdf',
    'OBGYN': 'Watermarked_Gynaecology_Obstetrics_Prepladder.pdf',
    'Medicine': 'Watermarked_Medicine_Prepladder.pdf',
    'Microbiology': 'Watermarked_Microbiology_Prepladder.pdf',
    'Ophthalmology': 'Watermarked_Ophthalmology_Prepladder.pdf',
    'Orthopaedics': 'Watermarked_Orthopaedics_Prepladder.pdf',
    'Pathology': 'Watermarked_Pathology_Prepladder.pdf',
    'Pediatrics': 'Watermarked_Pediatrics_Prepladder.pdf',
    'Pharmacology': 'Pharmacology Prepladder Version X Qbank.pdf',
    'Physiology': 'Physiology Prepladder Version X Qbank.pdf',
    'PSM': 'Watermarked_PSM_Prepladder.pdf',
    'Psychiatry': 'Watermarked_Psychiatry_Prepladder.pdf',
    'Radiology': 'Watermarked_Radiology_Prepladder.pdf',
    'Surgery': 'Watermarked_Surgery_Prepladder.pdf'
}

KEYWORDS = [
    "image", "given below", "shown", "arrow", "marked", "labeled", 
    "labelled", "diagram", "identify", "depicted", "picture", "scan", 
    "radiograph", "x-ray", "ct", "figure", "mri", "histology", "finding"
]

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

with open("prep_mcq_data.json", "r", encoding="utf-8") as f:
    prep_data = json.load(f)

t0 = time.time()
total_images_assigned = 0
total_images_saved = 0

for subj_name, sdata in prep_data.items():
    pdf_filename = PDF_MAP.get(subj_name)
    if not pdf_filename:
        print(f"Skipping {subj_name} (no PDF mapped)")
        continue
    pdf_path = os.path.join("prep", pdf_filename)
    if not os.path.exists(pdf_path):
        print(f"PDF missing: {pdf_path}")
        continue
        
    print(f"\n--- Processing {subj_name} ({pdf_filename}) ---")
    reader = PyPDF2.PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    toc = parse_toc(reader)
    if not toc:
        print(f"  WARNING: No TOC for {subj_name}")
        continue
        
    subj_slug = subj_name.lower().replace(" ", "_").replace("&", "")
    img_dir = f"images/prep/{subj_slug}"
    os.makedirs(img_dir, exist_ok=True)
    
    # Pre-extract all images from question pages
    page_images = {}
    
    # Group mcqs by chapter_num
    mcqs = sdata.get("mcqs", [])
    by_chap = {}
    for q in mcqs:
        # Reset images array
        q["images"] = []
        by_chap.setdefault(q.get("chapter_num", 1), []).append(q)
        
    subj_assigned = 0
    
    for i, (ch_num, ch_title, start_page) in enumerate(toc):
        end_page = toc[i+1][2] - 1 if i+1 < len(toc) else total_pages
        if end_page < start_page:
            end_page = start_page
            
        # Find where solutions start in this chapter
        sol_start_page = end_page
        chapter_pages = []
        for p_num in range(start_page, end_page + 1):
            if p_num <= total_pages:
                txt = reader.pages[p_num - 1].extract_text() or ""
                txt_clean = re.sub(r'Prepladder X Qbank\s+.*?Page \d+ of \d+', '', txt)
                chapter_pages.append((p_num, txt_clean))
                if ('Correct Answers' in txt or 'Solution for Question 1:' in txt) and sol_start_page == end_page:
                    sol_start_page = p_num

        # Question pages are from start_page to sol_start_page
        # Extract images from these question pages
        for p_num in range(start_page, min(sol_start_page + 1, total_pages + 1)):
            if p_num not in page_images:
                page = reader.pages[p_num - 1]
                if hasattr(page, 'images') and len(page.images) > 0:
                    imgs_on_page = []
                    for img_idx, img in enumerate(page.images):
                        img_name = f"p{p_num}_{img_idx}.jpg"
                        img_path = os.path.join(img_dir, img_name)
                        rel_path = f"images/prep/{subj_slug}/{img_name}"
                        if not os.path.exists(img_path) or os.path.getsize(img_path) == 0:
                            try:
                                with open(img_path, 'wb') as img_f:
                                    img_f.write(img.data)
                                total_images_saved += 1
                            except Exception:
                                pass
                        imgs_on_page.append(rel_path)
                    if imgs_on_page:
                        page_images[p_num] = imgs_on_page

        ch_qs = by_chap.get(ch_num, [])
        if not ch_qs:
            continue
            
        # Map questions to pages within this chapter
        q_on_pages = {}
        q_obj_map = {q.get("q_num"): q for q in ch_qs}
        
        for p_num, p_txt in chapter_pages:
            if p_num > sol_start_page:
                continue
            m_list = list(re.finditer(r'(?:^|\n)(\d+)\.\s*(.*?)(?=\n\d+\.|\Z)', p_txt, re.DOTALL))
            for m in m_list:
                qn = int(m.group(1))
                if qn in q_obj_map:
                    q_on_pages.setdefault(qn, []).append(p_num)
                    
        # Now match images to questions page by page
        # Each image is used AT MOST ONCE
        used_images_in_ch = set()
        
        for p_num in range(start_page, min(sol_start_page + 1, total_pages + 1)):
            imgs = page_images.get(p_num, [])
            if not imgs:
                continue
                
            # Candidate questions on this page
            cands = [qn for qn, plist in q_on_pages.items() if p_num in plist]
            # Also check if a question on previous page asked for an image and got none
            prev_cands = [qn for qn, plist in q_on_pages.items() if (p_num - 1) in plist and not q_obj_map[qn]["images"]]
            for qn in prev_cands:
                qtext = q_obj_map[qn].get("question", "").lower()
                if any(k in qtext for k in KEYWORDS):
                    cands.insert(0, qn)
                    
            # Filter candidates that mention image keywords and don't yet have an image
            kw_cands = [qn for qn in cands if any(k in q_obj_map[qn].get("question", "").lower() for k in KEYWORDS) and not q_obj_map[qn]["images"]]
            
            for img in imgs:
                if img in used_images_in_ch:
                    continue
                assigned_q = None
                if kw_cands:
                    assigned_q = kw_cands.pop(0)
                elif len(cands) == 1 and not q_obj_map[cands[0]]["images"]:
                    assigned_q = cands[0]
                    
                if assigned_q and assigned_q in q_obj_map:
                    q_obj_map[assigned_q]["images"].append(img)
                    used_images_in_ch.add(img)
                    subj_assigned += 1
                    total_images_assigned += 1

    print(f"  {subj_name}: {subj_assigned} questions assigned with unique images (0 duplicates)")

# Save updated prep_mcq_data.json
with open("prep_mcq_data.json", "w", encoding="utf-8") as f:
    json.dump(prep_data, f, ensure_ascii=False)

print(f"\n==========================================")
print(f"FINISHED! Total questions assigned images: {total_images_assigned}")
print(f"Time taken: {time.time() - t0:.1f}s")
print(f"Saved updated prep_mcq_data.json successfully!")

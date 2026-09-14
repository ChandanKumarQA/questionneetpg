import os, sys, glob, re, json, time, io
import PyPDF2
from PIL import Image

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

def unescape_stream(st):
    def rep(m):
        try:
            return chr(int(m.group(1), 8))
        except:
            return m.group(0)
    return re.sub(r'\\([0-7]{1,3})', rep, st)

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

def save_image_robust(xo, out_path):
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
            # Indexed
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
    except Exception as e:
        return False

def score_question(q):
    text = q.get('question', '').strip()
    score = len(text)
    if text.endswith('?') or '?' in text: score += 100
    if text.endswith(':') or text.endswith('__'): score += 50
    opts = q.get('options', {})
    if len(opts) == 4: score += 50
    opt_lens = sum(len(v) for v in opts.values())
    score += opt_lens
    if 'Search On Tg' in text: score -= 50
    if text.startswith('Match') or 'A-1' in text: score += 20
    if len(text.split()) < 5: score -= 100
    return score

def deduplicate_mcqs(mcqs):
    by_key = {}
    for idx, q in enumerate(mcqs):
        key = (q.get('chapter_num', 1), q.get('q_num', 1))
        by_key.setdefault(key, []).append((idx, q))
        
    clean_mcqs = []
    for key, q_list in by_key.items():
        if len(q_list) == 1:
            clean_mcqs.append(q_list[0])
        else:
            scored = sorted(q_list, key=lambda item: score_question(item[1]), reverse=True)
            clean_mcqs.append(scored[0])
            
    clean_mcqs.sort(key=lambda item: item[0])
    return [item[1] for item in clean_mcqs]

def main():
    with open("prep_mcq_data.json", "r", encoding="utf-8") as f:
        prep_data = json.load(f)

    t0 = time.time()
    total_q_imgs_assigned = 0
    total_sol_imgs_assigned = 0
    total_deduped_removed = 0

    token_pat = re.compile(
        r'(/Im\w+\s+Do)|'
        r'(?:^|\n|\()(\d+)\.\s+|'
        r'(?:^|\n)Correct\s+Answers?[\s:]|'
        r'(?:^|\n|\()Solution\s+for\s+Question\s*(\d+)',
        re.I
    )

    for subj_name, sdata in prep_data.items():
        pdf_filename = PDF_MAP.get(subj_name)
        if not pdf_filename:
            print(f"Skipping {subj_name} (no PDF mapped)")
            continue
        pdf_path = os.path.join("prep", pdf_filename)
        if not os.path.exists(pdf_path):
            print(f"PDF missing: {pdf_path}")
            continue

        subj_slug = subj_name.lower().replace(" ", "_").replace("&", "")
        img_dir = f"images/prep/{subj_slug}"
        os.makedirs(img_dir, exist_ok=True)

        reader = PyPDF2.PdfReader(pdf_path)
        total_pages = len(reader.pages)
        toc = parse_toc(reader)
        if not toc:
            print(f"  WARNING: No TOC for {subj_name}")
            continue

        raw_mcqs = sdata.get("mcqs", [])
        clean_mcqs = deduplicate_mcqs(raw_mcqs)
        removed_count = len(raw_mcqs) - len(clean_mcqs)
        total_deduped_removed += removed_count
        sdata["mcqs"] = clean_mcqs

        by_chap = {}
        for q in clean_mcqs:
            q["images"] = []
            q["solution_images"] = []
            by_chap.setdefault(q.get("chapter_num", 1), []).append(q)

        subj_q_imgs = 0
        subj_sol_imgs = 0

        for i, (ch_num, ch_title, start_page) in enumerate(toc):
            end_page = toc[i+1][2] - 1 if i+1 < len(toc) else total_pages
            if end_page < start_page:
                end_page = start_page

            ch_qs = by_chap.get(ch_num, [])
            if not ch_qs:
                continue

            valid_q_nums = set(q['q_num'] for q in ch_qs)
            q_obj_map = {q['q_num']: q for q in ch_qs}

            cur_q = None
            cur_sol = None
            in_sol = False

            q_imgs_map = {}   # qn -> [(p_num, img_name, xo)]
            sol_imgs_map = {} # qn -> [(p_num, img_name, xo)]

            for p_num in range(start_page, min(end_page + 1, total_pages + 1)):
                p = reader.pages[p_num - 1]
                contents = p.get_contents()
                if contents is None:
                    continue
                try:
                    if isinstance(contents, list):
                        st = b''.join(c.get_data() for c in contents).decode('latin-1', errors='replace')
                    else:
                        st = contents.get_data().decode('latin-1', errors='replace')
                except Exception:
                    continue

                st_clean = unescape_stream(st)
                xobjs = p.get('/Resources', {}).get('/XObject', {})

                for m in token_pat.finditer(st_clean):
                    tok = m.group(0).strip()
                    img_match = re.match(r'/(\w+)\s+Do', tok)
                    q_match = re.match(r'\(?(\d+)\.\s*$', tok)
                    sol_match = re.search(r'Solution\s+for\s+Question\s*(\d+)', tok, re.I)
                    ca_match = re.search(r'Correct\s+Answer', tok, re.I)

                    if sol_match:
                        in_sol = True
                        cur_sol = int(sol_match.group(1))
                    elif ca_match and not in_sol:
                        in_sol = True
                    elif q_match and not in_sol:
                        cand = int(q_match.group(1))
                        if cur_q is None:
                            if cand in valid_q_nums:
                                cur_q = cand
                        else:
                            if cand in valid_q_nums and cand > cur_q:
                                cur_q = cand
                    elif img_match:
                        img_name = img_match.group(1)
                        xo = xobjs.get(f'/{img_name}')
                        if xo:
                            if not in_sol and cur_q is not None:
                                q_imgs_map.setdefault(cur_q, []).append((p_num, img_name, xo))
                            elif in_sol and cur_sol is not None:
                                sol_imgs_map.setdefault(cur_sol, []).append((p_num, img_name, xo))

            # Now save question images and assign paths
            for qn, img_items in q_imgs_map.items():
                if qn in q_obj_map:
                    q = q_obj_map[qn]
                    saved_paths = []
                    for idx, (p_num, img_name, xo) in enumerate(img_items):
                        if len(img_items) > 1:
                            rel_path = f"images/prep/{subj_slug}/ch{ch_num}_q{qn}_{idx+1}.jpg"
                        else:
                            rel_path = f"images/prep/{subj_slug}/ch{ch_num}_q{qn}.jpg"
                        out_path = os.path.join(rel_path)
                        if save_image_robust(xo, out_path):
                            saved_paths.append(rel_path)
                            subj_q_imgs += 1
                            total_q_imgs_assigned += 1
                    q["images"] = saved_paths

            # Save solution images and assign paths
            for qn, img_items in sol_imgs_map.items():
                if qn in q_obj_map:
                    q = q_obj_map[qn]
                    saved_paths = []
                    for idx, (p_num, img_name, xo) in enumerate(img_items):
                        if len(img_items) > 1:
                            rel_path = f"images/prep/{subj_slug}/ch{ch_num}_q{qn}_sol_{idx+1}.jpg"
                        else:
                            rel_path = f"images/prep/{subj_slug}/ch{ch_num}_q{qn}_sol.jpg"
                        out_path = os.path.join(rel_path)
                        if save_image_robust(xo, out_path):
                            saved_paths.append(rel_path)
                            subj_sol_imgs += 1
                            total_sol_imgs_assigned += 1
                    q["solution_images"] = saved_paths

        print(f"✓ {subj_name}: {subj_q_imgs} Q-images, {subj_sol_imgs} Sol-images assigned (0 keyword heuristics, 100% stream order)")

    with open("prep_mcq_data.json", "w", encoding="utf-8") as f:
        json.dump(prep_data, f, ensure_ascii=False)

    print(f"\n==========================================")
    print(f"FINISHED PREPLADDER REASSIGNMENT!")
    print(f"Total Question Images: {total_q_imgs_assigned}")
    print(f"Total Solution Images: {total_sol_imgs_assigned}")
    print(f"Time taken: {time.time() - t0:.1f}s")
    print(f"Saved updated prep_mcq_data.json successfully!")

if __name__ == '__main__':
    main()

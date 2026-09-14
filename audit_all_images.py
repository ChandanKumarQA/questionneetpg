import os, sys, json

def audit_dataset(json_path, dataset_name):
    print(f"\n==========================================")
    print(f"AUDITING {dataset_name} ({json_path})")
    print(f"==========================================")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    total_mcqs = 0
    with_q_imgs = 0
    with_sol_imgs = 0
    total_q_imgs = 0
    total_sol_imgs = 0
    
    missing_files = []
    zero_byte_files = []
    
    # Check uniqueness of question images across questions
    img_to_q = {} # img_path -> (subj, q_id)
    duplicates = []
    
    for subj, sdata in data.items():
        mcqs = sdata.get('mcqs', [])
        for q in mcqs:
            total_mcqs += 1
            qid = q.get('id', f"{subj}_Q{q.get('q_num')}")
            
            q_imgs = q.get('images') or []
            if q_imgs:
                with_q_imgs += 1
                total_q_imgs += len(q_imgs)
                for img_path in q_imgs:
                    if not os.path.exists(img_path):
                        missing_files.append((qid, img_path))
                    elif os.path.getsize(img_path) == 0:
                        zero_byte_files.append((qid, img_path))
                    else:
                        if img_path in img_to_q:
                            duplicates.append((img_path, img_to_q[img_path], (subj, qid)))
                        else:
                            img_to_q[img_path] = (subj, qid)
                            
            sol_imgs = q.get('solution_images') or []
            if sol_imgs:
                with_sol_imgs += 1
                total_sol_imgs += len(sol_imgs)
                for img_path in sol_imgs:
                    if not os.path.exists(img_path):
                        missing_files.append((qid, img_path))
                    elif os.path.getsize(img_path) == 0:
                        zero_byte_files.append((qid, img_path))

    print(f"Total MCQs: {total_mcqs}")
    print(f"MCQs with Question Images: {with_q_imgs} (Total Q-Images: {total_q_imgs})")
    print(f"MCQs with Solution Images: {with_sol_imgs} (Total Sol-Images: {total_sol_imgs})")
    print(f"Missing Image Files: {len(missing_files)}")
    print(f"0-Byte Image Files: {len(zero_byte_files)}")
    print(f"Duplicate Image Collisions: {len(duplicates)}")
    
    if missing_files:
        print(f"Sample missing files (first 5): {missing_files[:5]}")
    if duplicates:
        print(f"Sample duplicates (first 5): {duplicates[:5]}")
        
    assert len(missing_files) == 0, f"Found {len(missing_files)} missing files in {dataset_name}!"
    assert len(zero_byte_files) == 0, f"Found {len(zero_byte_files)} zero-byte files in {dataset_name}!"
    assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate image assignments in {dataset_name}!"
    print(f"✓ {dataset_name} PASSED ALL INTEGRITY AUDITS!")

def check_spot_checks():
    print(f"\n==========================================")
    print("VERIFYING KEY CLINICAL SPOT-CHECKS")
    print(f"==========================================")
    
    with open('prep_mcq_data.json') as f:
        prep = json.load(f)
    with open('mcq_data.json') as f:
        marrow = json.load(f)
        
    checks = [
        # Dataset, Subject, Ch, Q, ExpectImage, Description
        ('PrepLadder', prep, 'Anatomy', 1, 3, False, "Neural tube statements (text only)"),
        ('PrepLadder', prep, 'Anatomy', 1, 5, True, "Anencephaly skull structural abnormality"),
        ('PrepLadder', prep, 'Anatomy', 1, 11, True, "Labelled structures diagram"),
        ('PrepLadder', prep, 'Anaesthesia', 14, 2, False, "ET tube placement verification (text only)"),
        ('PrepLadder', prep, 'Anaesthesia', 14, 3, True, "Capnograph waveform"),
        ('PrepLadder', prep, 'Anaesthesia', 14, 4, True, "ECG waveform"),
        ('PrepLadder', prep, 'Anaesthesia', 14, 5, False, "PFT results criteria (text only)"),
        ('PrepLadder', prep, 'Anaesthesia', 14, 7, True, "Device shown in given image"),
        ('PrepLadder', prep, 'Surgery', 1, 1, True, "Paget disease breast picture"),
        ('PrepLadder', prep, 'Surgery', 3, 4, True, "CT image of breast condition"),
        ('Marrow', marrow, 'Pharmacology', 14, 18, True, "PSVT ECG waveform (Indirect Indexed)"),
    ]
    
    all_passed = True
    for ds_name, ds, subj, ch, qn, expect_img, desc in checks:
        matched = None
        for q in ds[subj]['mcqs']:
            if q.get('chapter_num') == ch and q.get('q_num') == qn:
                matched = q
                break
        if not matched:
            print(f"❌ {ds_name} {subj} Ch{ch} Q{qn}: Question NOT found!")
            all_passed = False
            continue
            
        imgs = matched.get('images') or []
        has_img = len(imgs) > 0
        if has_img == expect_img:
            status = "✓ PASS"
            img_info = f"-> {imgs}" if has_img else "-> (strictly empty [])"
            print(f"{status}: [{ds_name}] {subj} Ch{ch} Q{qn} ({desc}) {img_info}")
        else:
            status = "❌ FAIL"
            print(f"{status}: [{ds_name}] {subj} Ch{ch} Q{qn} ({desc}) Expected has_img={expect_img}, got {imgs}")
            all_passed = False
            
    assert all_passed, "Spot checks failed!"
    print("\n✓ ALL CLINICAL SPOT-CHECKS PASSED PERFECTLY!")

if __name__ == '__main__':
    audit_dataset('prep_mcq_data.json', 'PrepLadder')
    audit_dataset('mcq_data.json', 'Marrow ED8')
    check_spot_checks()

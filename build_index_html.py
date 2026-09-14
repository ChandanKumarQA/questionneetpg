import json, os

print("Building index.html with Dual Platform Support: Marrow ED8 & PrepLadder VX...")

with open('mcq_data.json', 'r', encoding='utf-8') as f:
    marrow_raw = json.load(f)

with open('prep_mcq_data.json', 'r', encoding='utf-8') as f:
    prep_raw = json.load(f)

# Subject metadata
SUBJECT_META = {
    "Anaesthesia": {"icon": "💉", "color": "#06b6d4", "grad": "linear-gradient(135deg, #06b6d4, #0284c7)", "desc": "Airway, general & regional anaesthesia, ICU drugs, pain & monitoring"},
    "Anatomy": {"icon": "🦷", "color": "#7c3aed", "grad": "linear-gradient(135deg, #7c3aed, #5b21b6)", "desc": "Gross anatomy, embryology, histology, neuroanatomy & osteology"},
    "Biochemistry": {"icon": "🧬", "color": "#8b5cf6", "grad": "linear-gradient(135deg, #8b5cf6, #6366f1)", "desc": "Metabolism, enzymes, genetics, molecular biology & clinical biochem"},
    "Dermatology": {"icon": "🩹", "color": "#f472b6", "grad": "linear-gradient(135deg, #f472b6, #db2777)", "desc": "Skin infections, immunological disorders, STDs, hair & nail diseases"},
    "ENT": {"icon": "👂", "color": "#ec4899", "grad": "linear-gradient(135deg, #ec4899, #d946ef)", "desc": "Otology, rhinology, laryngology, neck masses & operative instruments"},
    "Forensic Medicine": {"icon": "⚖️", "color": "#f59e0b", "grad": "linear-gradient(135deg, #f59e0b, #d97706)", "desc": "Thanatology, toxicology, forensic pathology, medical jurisprudence"},
    "Medicine": {"icon": "🩺", "color": "#0ea5e9", "grad": "linear-gradient(135deg, #0ea5e9, #0369a1)", "desc": "Cardiology, neurology, nephrology, endocrinology, rheumatology & more"},
    "Microbiology": {"icon": "🦠", "color": "#22c55e", "grad": "linear-gradient(135deg, #22c55e, #15803d)", "desc": "Bacteriology, virology, mycology, parasitology & immunology"},
    "OBGYN": {"icon": "🤰", "color": "#e879f9", "grad": "linear-gradient(135deg, #e879f9, #c026d3)", "desc": "Obstetrics, gynaecology, reproductive medicine & neonatology"},
    "Ophthalmology": {"icon": "👁️", "color": "#10b981", "grad": "linear-gradient(135deg, #10b981, #059669)", "desc": "Cornea, retina, glaucoma, optics, neuro-ophthalmology & surgery"},
    "Orthopaedics": {"icon": "🦴", "color": "#3b82f6", "grad": "linear-gradient(135deg, #3b82f6, #2563eb)", "desc": "Trauma, fractures, pediatric ortho, bone tumours, sports injuries"},
    "PSM": {"icon": "🏥", "color": "#14b8a6", "grad": "linear-gradient(135deg, #14b8a6, #0d9488)", "desc": "Epidemiology, biostatistics, national health programs, screening"},
    "Pathology": {"icon": "🔬", "color": "#ef4444", "grad": "linear-gradient(135deg, #ef4444, #b91c1c)", "desc": "General & systemic pathology, haematology, clinical pathology"},
    "Pediatrics": {"icon": "👶", "color": "#fbbf24", "grad": "linear-gradient(135deg, #fbbf24, #d97706)", "desc": "Growth & development, neonatology, infectious diseases, nutrition"},
    "Pharmacology": {"icon": "💊", "color": "#f43f5e", "grad": "linear-gradient(135deg, #f43f5e, #e11d48)", "desc": "ANS, CVS, CNS, chemotherapy, antimicrobials, toxicology & kinetics"},
    "Physiology": {"icon": "🫀", "color": "#eab308", "grad": "linear-gradient(135deg, #eab308, #ca8a04)", "desc": "General physiology, nerve-muscle, CVS, respiratory, renal, endocrinology"},
    "Psychiatry": {"icon": "🧠", "color": "#a855f7", "grad": "linear-gradient(135deg, #a855f7, #9333ea)", "desc": "Psychosis, mood disorders, neurosis, psychoanalysis, substance abuse"},
    "Radiology": {"icon": "📡", "color": "#38bdf8", "grad": "linear-gradient(135deg, #38bdf8, #0284c7)", "desc": "X-ray, CT, MRI, ultrasound, nuclear medicine & interventional radiology"},
    "Surgery": {"icon": "🔪", "color": "#fb923c", "grad": "linear-gradient(135deg, #fb923c, #ea580c)", "desc": "General surgery, GI, hepatobiliary, endocrine, vascular & trauma surgery"}
}

def build_payload(raw_data):
    payload = {}
    tot_mcqs = 0
    tot_ibqs = 0
    for subj, subj_data in raw_data.items():
        meta = SUBJECT_META.get(subj, {"icon": "📚", "color": "#3b82f6", "grad": "linear-gradient(135deg, #3b82f6, #6366f1)", "desc": "Medical review"})
        all_mcqs = subj_data.get('mcqs', [])
        ibq_c = sum(1 for q in all_mcqs if q.get("images"))
        tot_ibqs += ibq_c
        tot_mcqs += len(all_mcqs)
        chs_count = subj_data.get('chapters_count') or len(set(q.get('chapter', '') for q in all_mcqs))
        payload[subj] = {
            "icon": meta["icon"],
            "color": meta["color"],
            "grad": meta["grad"],
            "total_pdf_questions": len(all_mcqs),
            "chapters_count": chs_count,
            "desc": meta["desc"],
            "ibq_count": ibq_c,
            "mcqs": all_mcqs
        }
    return payload, tot_mcqs, tot_ibqs

marrow_payload, marrow_total_mcqs, marrow_total_ibqs = build_payload(marrow_raw)
prep_payload, prep_total_mcqs, prep_total_ibqs = build_payload(prep_raw)

print(f"Marrow: {marrow_total_mcqs} MCQs ({marrow_total_ibqs} IBQs) across {len(marrow_payload)} subjects")
print(f"PrepLadder: {prep_total_mcqs} MCQs ({prep_total_ibqs} IBQs) across {len(prep_payload)} subjects")
print(f"Grand Total: {marrow_total_mcqs + prep_total_mcqs} MCQs across both platforms!")

marrow_json_str = json.dumps(marrow_payload, ensure_ascii=False)
prep_json_str = json.dumps(prep_payload, ensure_ascii=False)

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Medicus ED8 • Medical MCQ Mastery</title>
  <meta name="description" content="Medical Entrance Platform with 16,040+ authentic MCQs, verified answer keys, detailed clinical explanations, and high-resolution clinical images/radiology across all 19 ED8 specialties." />
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />

  <style>
    :root {{
      --bg-dark: #070a12;
      --bg-card: rgba(18, 24, 38, 0.75);
      --bg-card-hover: rgba(28, 36, 56, 0.85);
      --border-card: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(56, 189, 248, 0.5);
      
      --cyan: #06b6d4;
      --indigo: #6366f1;
      --purple: #a855f7;
      --emerald: #10b981;
      --rose: #f43f5e;
      --amber: #f59e0b;

      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;

      --grad-primary: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
      --grad-emerald: linear-gradient(135deg, #10b981 0%, #059669 100%);
      --grad-rose: linear-gradient(135deg, #f43f5e 0%, #be123c 100%);

      --font-body: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-heading: 'Outfit', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;

      --radius-sm: 8px;
      --radius-md: 14px;
      --radius-lg: 20px;
      --radius-full: 9999px;

      --shadow-card: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: var(--font-body);
      background-color: var(--bg-dark);
      color: var(--text-main);
      min-height: 100vh;
      overflow-x: hidden;
      line-height: 1.6;
      position: relative;
    }}

    /* Ambient background orbs */
    .orb {{
      position: fixed;
      border-radius: 50%;
      filter: blur(120px);
      pointer-events: none;
      z-index: 0;
      opacity: 0.35;
      animation: float 20s infinite alternate ease-in-out;
    }}
    .orb-1 {{ width: 500px; height: 500px; background: #06b6d4; top: -100px; left: -100px; }}
    .orb-2 {{ width: 600px; height: 600px; background: #6366f1; top: 30%; right: -150px; animation-duration: 25s; }}
    .orb-3 {{ width: 450px; height: 450px; background: #ec4899; bottom: -50px; left: 20%; animation-duration: 18s; }}

    @keyframes float {{
      0% {{ transform: translate(0, 0) scale(1); }}
      100% {{ transform: translate(50px, 40px) scale(1.08); }}
    }}

    .app-wrap {{
      position: relative;
      z-index: 1;
      max-width: 1280px;
      margin: 0 auto;
      padding: 24px 20px 80px;
    }}

    /* Top Navbar */
    .navbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 24px;
      background: rgba(15, 23, 42, 0.65);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      margin-bottom: 32px;
      box-shadow: var(--shadow-card);
    }}

    .logo-area {{
      display: flex;
      align-items: center;
      gap: 14px;
      text-decoration: none;
      cursor: pointer;
    }}
    .logo-badge {{
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: var(--grad-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);
    }}
    .logo-text h1 {{
      font-family: var(--font-heading);
      font-size: 20px;
      font-weight: 700;
      letter-spacing: -0.02em;
      background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .logo-text p {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--cyan);
      font-weight: 600;
    }}

    /* Platform Switcher Control */
    .platform-switcher {{
      display: flex;
      align-items: center;
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 40px;
      padding: 4px;
      gap: 4px;
      box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4);
    }}
    .platform-btn {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: transparent;
      color: var(--text-dim);
      border: none;
      border-radius: 36px;
      padding: 8px 18px;
      font-family: var(--font-body);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      user-select: none;
    }}
    .platform-btn:hover {{
      color: #fff;
      background: rgba(255, 255, 255, 0.06);
    }}
    .platform-btn.active {{
      background: linear-gradient(135deg, #0284c7, #6366f1);
      color: #ffffff;
      box-shadow: 0 4px 18px rgba(99, 102, 241, 0.45);
    }}
    .platform-btn.active.prep-active {{
      background: linear-gradient(135deg, #f59e0b, #ef4444);
      box-shadow: 0 4px 18px rgba(245, 158, 11, 0.45);
    }}
    .platform-btn .p-badge {{
      font-size: 10px;
      padding: 2px 7px;
      border-radius: 10px;
      background: rgba(0, 0, 0, 0.3);
      font-weight: 700;
      letter-spacing: 0.5px;
    }}
    .platform-btn .p-count {{
      font-size: 11px;
      opacity: 0.85;
      font-weight: 500;
    }}

    .nav-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .badge-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: var(--radius-full);
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      font-size: 12px;
      font-weight: 500;
      color: var(--text-muted);
    }}
    .badge-pill.cyan {{
      background: rgba(6, 182, 212, 0.1);
      border-color: rgba(6, 182, 212, 0.25);
      color: var(--cyan);
    }}
    .badge-pill.emerald {{
      background: rgba(16, 185, 129, 0.1);
      border-color: rgba(16, 185, 129, 0.25);
      color: var(--emerald);
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 10px 18px;
      border-radius: var(--radius-md);
      font-family: var(--font-body);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      user-select: none;
      text-decoration: none;
    }}
    .btn:active {{ transform: scale(0.98); }}
    .btn-primary {{
      background: var(--grad-primary);
      color: #fff;
      box-shadow: 0 4px 20px -2px rgba(6, 182, 212, 0.4);
    }}
    .btn-primary:hover {{
      box-shadow: 0 6px 25px rgba(6, 182, 212, 0.6);
      transform: translateY(-1px);
    }}
    .btn-glass {{
      background: rgba(255, 255, 255, 0.05);
      border-color: var(--border-card);
      color: var(--text-main);
    }}
    .btn-glass:hover {{
      background: rgba(255, 255, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.2);
    }}
    .btn-icon {{
      width: 40px;
      height: 40px;
      padding: 0;
      border-radius: var(--radius-md);
    }}

    /* HERO SECTION */
    .hero-banner {{
      position: relative;
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.7) 100%);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 36px 32px;
      margin-bottom: 32px;
      box-shadow: var(--shadow-card);
      overflow: hidden;
    }}
    .hero-banner::after {{
      content: '';
      position: absolute;
      top: -50%;
      right: -10%;
      width: 400px;
      height: 400px;
      background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
      pointer-events: none;
    }}

    .hero-content {{
      position: relative;
      z-index: 1;
      max-width: 800px;
    }}
    .hero-tag {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      background: rgba(6, 182, 212, 0.15);
      border: 1px solid rgba(6, 182, 212, 0.3);
      border-radius: var(--radius-full);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: var(--cyan);
      text-transform: uppercase;
      margin-bottom: 14px;
    }}
    .hero-title {{
      font-family: var(--font-heading);
      font-size: clamp(28px, 4vw, 38px);
      font-weight: 800;
      letter-spacing: -0.02em;
      line-height: 1.2;
      margin-bottom: 12px;
      background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 60%, #94a3b8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .hero-desc {{
      color: var(--text-muted);
      font-size: 15px;
      margin-bottom: 24px;
      line-height: 1.6;
    }}

    /* Stats Ribbon */
    .stats-ribbon {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 16px;
      margin-bottom: 28px;
    }}
    .stat-card {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-md);
      padding: 14px 18px;
      transition: all 0.2s ease;
    }}
    .stat-card:hover {{
      background: rgba(255, 255, 255, 0.06);
      border-color: rgba(255, 255, 255, 0.15);
    }}
    .stat-val {{
      font-family: var(--font-mono);
      font-size: 24px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: baseline;
      gap: 4px;
    }}
    .stat-val span {{
      font-size: 14px;
      color: var(--cyan);
      font-weight: 500;
    }}
    .stat-lbl {{
      font-size: 12px;
      color: var(--text-dim);
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-top: 2px;
    }}

    /* Action Banners */
    .action-banners-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 20px;
      margin-bottom: 36px;
    }}
    .feature-card {{
      border-radius: var(--radius-lg);
      padding: 24px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 20px;
      box-shadow: var(--shadow-card);
    }}
    .grand-mock-card {{
      background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(6, 182, 212, 0.15) 100%);
      border: 1px solid rgba(99, 102, 241, 0.3);
    }}
    .ibq-card {{
      background: linear-gradient(135deg, rgba(236, 72, 153, 0.2) 0%, rgba(168, 85, 247, 0.15) 100%);
      border: 1px solid rgba(236, 72, 153, 0.3);
    }}
    .feature-info h3 {{
      font-family: var(--font-heading);
      font-size: 18px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .feature-info p {{
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 4px;
    }}
    .feature-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    /* Controls Bar */
    .controls-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 24px;
    }}
    .search-box {{
      position: relative;
      flex: 1;
      min-width: 260px;
      max-width: 420px;
    }}
    .search-box input {{
      width: 100%;
      padding: 12px 16px 12px 42px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-md);
      color: #fff;
      font-family: var(--font-body);
      font-size: 13px;
      outline: none;
      transition: all 0.2s ease;
    }}
    .search-box input:focus {{
      background: rgba(255, 255, 255, 0.08);
      border-color: var(--cyan);
      box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.15);
    }}
    .search-icon {{
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-dim);
      font-size: 16px;
      pointer-events: none;
    }}

    .config-pills {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .pill-group {{
      display: flex;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-md);
      padding: 4px;
    }}
    .pill-opt {{
      padding: 6px 14px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: all 0.2s ease;
      user-select: none;
    }}
    .pill-opt.active {{
      background: var(--grad-primary);
      color: #fff;
      box-shadow: 0 2px 10px rgba(6, 182, 212, 0.3);
    }}

    /* Subject Grid */
    .subject-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 20px;
    }}
    .subject-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 24px;
      cursor: pointer;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-height: 230px;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: var(--shadow-card);
    }}
    .subject-card:hover {{
      transform: translateY(-4px);
      background: var(--bg-card-hover);
      border-color: rgba(255, 255, 255, 0.18);
      box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.6);
    }}
    .subject-card::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: var(--card-grad, var(--grad-primary));
      opacity: 0.8;
    }}
    .subj-header {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      margin-bottom: 12px;
    }}
    .subj-icon {{
      width: 48px;
      height: 48px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
    }}
    .subj-meta-badges {{
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 4px;
    }}
    .subj-meta-badge {{
      font-family: var(--font-mono);
      font-size: 11px;
      padding: 3px 8px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-full);
      color: var(--text-muted);
    }}
    .subj-meta-badge.ibq {{
      background: rgba(236, 72, 153, 0.15);
      border-color: rgba(236, 72, 153, 0.3);
      color: #f472b6;
      font-weight: 600;
    }}
    .subj-title {{
      font-family: var(--font-heading);
      font-size: 18px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 6px;
    }}
    .subj-desc {{
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.5;
      margin-bottom: 18px;
      flex-grow: 1;
    }}
    .subj-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 14px;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
    }}
    .subj-stat {{
      font-size: 12px;
      font-weight: 600;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .subj-stat span {{
      color: var(--cyan);
      font-family: var(--font-mono);
    }}
    .subj-start-btn {{
      padding: 6px 14px;
      font-size: 12px;
      font-weight: 700;
      border-radius: var(--radius-sm);
      background: rgba(255, 255, 255, 0.08);
      color: #fff;
      transition: all 0.2s;
    }}
    .subject-card:hover .subj-start-btn {{
      background: var(--card-grad, var(--grad-primary));
      box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    }}

    /* QUIZ VIEW */
    .quiz-view {{
      display: none;
      animation: fadeIn 0.3s ease;
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(8px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .quiz-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
      background: rgba(15, 23, 42, 0.8);
      backdrop-filter: blur(20px);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 16px 24px;
      margin-bottom: 24px;
      box-shadow: var(--shadow-card);
    }}
    .quiz-info-block {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .quiz-subject-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      background: rgba(6, 182, 212, 0.1);
      border: 1px solid rgba(6, 182, 212, 0.3);
      border-radius: var(--radius-md);
      font-size: 13px;
      font-weight: 700;
      color: #fff;
    }}
    .quiz-timer {{
      font-family: var(--font-mono);
      font-size: 16px;
      font-weight: 700;
      color: var(--amber);
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      background: rgba(245, 158, 11, 0.1);
      border: 1px solid rgba(245, 158, 11, 0.25);
      border-radius: var(--radius-md);
    }}

    .progress-bar-wrap {{
      width: 100%;
      height: 6px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-full);
      overflow: hidden;
      margin-bottom: 24px;
    }}
    .progress-fill {{
      height: 100%;
      background: var(--grad-primary);
      width: 0%;
      transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .question-layout {{
      display: grid;
      grid-template-columns: 1fr 300px;
      gap: 24px;
      align-items: start;
    }}
    @media (max-width: 960px) {{
      .question-layout {{ grid-template-columns: 1fr; }}
    }}

    .question-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 32px;
      box-shadow: var(--shadow-card);
    }}
    .q-meta {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .q-number {{
      font-family: var(--font-mono);
      font-size: 13px;
      color: var(--cyan);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .q-chapter {{
      font-size: 12px;
      color: var(--text-dim);
      font-weight: 500;
    }}
    .chapter-dropdown-wrap {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .chapter-dropdown {{
      background: rgba(15, 23, 42, 0.9);
      color: var(--text-main);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 8px;
      padding: 6px 32px 6px 12px;
      font-family: var(--font-body);
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      outline: none;
      appearance: none;
      -webkit-appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%2394a3b8' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10z'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 10px center;
      min-width: 180px;
      max-width: 320px;
      transition: border-color 0.2s, box-shadow 0.2s;
    }}
    .chapter-dropdown:hover {{
      border-color: rgba(56, 189, 248, 0.4);
    }}
    .chapter-dropdown:focus {{
      border-color: var(--cyan);
      box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.15);
    }}
    .chapter-dropdown option {{
      background: #0f172a;
      color: #f8fafc;
      padding: 8px;
    }}
    .q-ibq-tag {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 10px;
      background: rgba(236, 72, 153, 0.15);
      border: 1px solid rgba(236, 72, 153, 0.3);
      border-radius: var(--radius-full);
      font-size: 11px;
      font-weight: 700;
      color: #f472b6;
    }}

    .q-text {{
      font-size: 18px;
      font-weight: 600;
      color: #fff;
      line-height: 1.6;
      margin-bottom: 24px;
      white-space: pre-wrap;
    }}

    /* CLINICAL IMAGE GALLERY */
    .q-images-wrap {{
      margin-bottom: 28px;
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      justify-content: center;
    }}
    .clinical-img-card {{
      position: relative;
      background: #020617;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: var(--radius-md);
      overflow: hidden;
      cursor: pointer;
      max-width: 480px;
      width: 100%;
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.6);
      transition: all 0.25s ease;
    }}
    .clinical-img-card:hover {{
      border-color: var(--cyan);
      transform: scale(1.01);
      box-shadow: 0 12px 35px rgba(6, 182, 212, 0.2);
    }}
    .clinical-img-card img {{
      width: 100%;
      height: auto;
      max-height: 360px;
      object-fit: contain;
      display: block;
      background: #fff;
    }}
    .img-zoom-hint {{
      position: absolute;
      bottom: 8px;
      right: 8px;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: var(--radius-sm);
      padding: 4px 8px;
      font-size: 11px;
      font-weight: 600;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 4px;
      pointer-events: none;
    }}

    /* Options List */
    .options-list {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 28px;
    }}
    .option-item {{
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 16px 20px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      user-select: none;
    }}
    .option-item:hover:not(.locked) {{
      background: rgba(255, 255, 255, 0.07);
      border-color: rgba(255, 255, 255, 0.15);
      transform: translateX(4px);
    }}
    .opt-key {{
      width: 34px;
      height: 34px;
      border-radius: var(--radius-sm);
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-mono);
      font-size: 13px;
      font-weight: 700;
      color: var(--text-muted);
      flex-shrink: 0;
      text-transform: uppercase;
      transition: all 0.2s;
    }}
    .opt-label {{
      font-size: 15px;
      font-weight: 500;
      color: var(--text-main);
      flex-grow: 1;
      white-space: pre-wrap;
    }}

    /* Selected state */
    .option-item.selected {{
      background: rgba(6, 182, 212, 0.12);
      border-color: var(--cyan);
    }}
    .option-item.selected .opt-key {{
      background: var(--cyan);
      color: #000;
      font-weight: 800;
    }}

    /* Correct/Wrong states */
    .option-item.correct {{
      background: rgba(16, 185, 129, 0.15) !important;
      border-color: var(--emerald) !important;
    }}
    .option-item.correct .opt-key {{
      background: var(--emerald) !important;
      color: #fff !important;
    }}
    .option-item.wrong {{
      background: rgba(244, 63, 94, 0.15) !important;
      border-color: var(--rose) !important;
    }}
    .option-item.wrong .opt-key {{
      background: var(--rose) !important;
      color: #fff !important;
    }}

    /* Explanation Box */
    .explanation-box {{
      display: none;
      background: rgba(6, 182, 212, 0.05);
      border: 1px solid rgba(6, 182, 212, 0.25);
      border-radius: var(--radius-md);
      padding: 22px 24px;
      margin-top: 24px;
      animation: fadeIn 0.3s ease;
    }}
    .exp-hdr {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-family: var(--font-heading);
      font-size: 15px;
      font-weight: 700;
      color: var(--cyan);
      margin-bottom: 12px;
    }}
    .exp-body {{
      font-size: 14px;
      line-height: 1.7;
      color: #cbd5e1;
      white-space: pre-wrap;
    }}
    .sol-images-wrap {{
      margin-top: 16px;
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .sol-img-card {{
      max-width: 380px;
      width: 100%;
      border-radius: var(--radius-sm);
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.1);
      cursor: pointer;
    }}
    .sol-img-card img {{
      width: 100%;
      display: block;
      background: #fff;
    }}

    /* Question Action Footer */
    .q-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
      padding-top: 20px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      margin-top: 24px;
    }}
    .q-nav-btns {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    /* Sidebar Palette */
    .quiz-sidebar {{
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 24px;
      box-shadow: var(--shadow-card);
      position: sticky;
      top: 24px;
    }}
    .palette-title {{
      font-family: var(--font-heading);
      font-size: 15px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .palette-grid {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 8px;
      max-height: 380px;
      overflow-y: auto;
      padding-right: 4px;
    }}
    .pal-btn {{
      height: 38px;
      border-radius: var(--radius-sm);
      border: 1px solid rgba(255, 255, 255, 0.08);
      background: rgba(255, 255, 255, 0.04);
      color: var(--text-muted);
      font-family: var(--font-mono);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      transition: all 0.2s;
    }}
    .pal-btn:hover {{
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
    }}
    .pal-btn.current {{
      border-color: var(--cyan);
      box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.4);
      color: #fff;
      font-weight: 800;
    }}
    .pal-btn.answered {{
      background: rgba(16, 185, 129, 0.2);
      border-color: rgba(16, 185, 129, 0.4);
      color: var(--emerald);
    }}
    .pal-btn.flagged {{
      background: rgba(245, 158, 11, 0.2);
      border-color: rgba(245, 158, 11, 0.4);
      color: var(--amber);
    }}
    .pal-btn.has-img::after {{
      content: '';
      position: absolute;
      top: 3px;
      right: 3px;
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: #f472b6;
    }}

    .pal-legend {{
      margin-top: 18px;
      padding-top: 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
      display: flex;
      flex-direction: column;
      gap: 8px;
      font-size: 11px;
      color: var(--text-dim);
    }}
    .leg-item {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .leg-dot {{
      width: 10px;
      height: 10px;
      border-radius: 3px;
    }}

    /* RESULTS VIEW */
    .results-view {{
      display: none;
      animation: fadeIn 0.4s ease;
    }}
    .results-banner {{
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.8) 100%);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 40px;
      margin-bottom: 32px;
      box-shadow: var(--shadow-card);
      text-align: center;
      position: relative;
      overflow: hidden;
    }}
    .score-circle {{
      width: 140px;
      height: 140px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 70%);
      border: 4px solid var(--cyan);
      box-shadow: 0 0 30px rgba(6, 182, 212, 0.4);
      margin: 0 auto 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }}
    .score-percent {{
      font-family: var(--font-mono);
      font-size: 34px;
      font-weight: 800;
      color: #fff;
    }}
    .score-label {{
      font-size: 11px;
      color: var(--cyan);
      text-transform: uppercase;
      font-weight: 600;
      letter-spacing: 0.1em;
    }}
    .results-title {{
      font-family: var(--font-heading);
      font-size: 28px;
      font-weight: 800;
      margin-bottom: 8px;
    }}
    .results-subtitle {{
      font-size: 14px;
      color: var(--text-muted);
      margin-bottom: 32px;
    }}

    .results-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 16px;
      max-width: 700px;
      margin: 0 auto 32px;
    }}
    .res-metric {{
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-md);
      padding: 16px;
    }}
    .res-metric-val {{
      font-family: var(--font-mono);
      font-size: 24px;
      font-weight: 700;
    }}
    .res-metric-val.green {{ color: var(--emerald); }}
    .res-metric-val.red {{ color: var(--rose); }}
    .res-metric-val.amber {{ color: var(--amber); }}
    .res-metric-val.cyan {{ color: var(--cyan); }}
    .res-metric-lbl {{
      font-size: 11px;
      color: var(--text-dim);
      text-transform: uppercase;
      font-weight: 600;
      margin-top: 4px;
    }}

    .review-filter-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 24px;
    }}
    .review-list {{
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}
    .review-item {{
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 24px;
    }}
    .rev-badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: var(--radius-full);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      margin-bottom: 12px;
    }}
    .rev-badge.correct {{
      background: rgba(16, 185, 129, 0.15);
      color: var(--emerald);
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    .rev-badge.wrong {{
      background: rgba(244, 63, 94, 0.15);
      color: var(--rose);
      border: 1px solid rgba(244, 63, 94, 0.3);
    }}
    .rev-badge.unanswered {{
      background: rgba(245, 158, 11, 0.15);
      color: var(--amber);
      border: 1px solid rgba(245, 158, 11, 0.3);
    }}

    /* Lightbox Modal */
    .lightbox-overlay {{
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.9);
      backdrop-filter: blur(15px);
      z-index: 200;
      align-items: center;
      justify-content: center;
      padding: 24px;
      cursor: zoom-out;
    }}
    .lightbox-content {{
      max-width: 90vw;
      max-height: 88vh;
      border-radius: var(--radius-md);
      overflow: hidden;
      box-shadow: 0 0 50px rgba(0, 0, 0, 0.8);
      position: relative;
      cursor: default;
    }}
    .lightbox-content img {{
      max-width: 100%;
      max-height: 85vh;
      display: block;
      border-radius: var(--radius-md);
      object-fit: contain;
      background: #fff;
    }}
    .lightbox-close {{
      position: absolute;
      top: -40px;
      right: 0;
      background: none;
      border: none;
      color: #fff;
      font-size: 28px;
      cursor: pointer;
    }}

    /* Modal */
    .modal-overlay {{
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(10px);
      z-index: 100;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}
    .modal-card {{
      background: #0f172a;
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: var(--radius-lg);
      padding: 32px;
      max-width: 440px;
      width: 100%;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.75);
      text-align: center;
    }}

    /* Toast */
    .toast {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: rgba(15, 23, 42, 0.95);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: var(--radius-md);
      padding: 12px 20px;
      color: #fff;
      font-size: 13px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
      z-index: 999;
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .toast.show {{
      transform: translateY(0);
      opacity: 1;
    }}

    #fileInput {{ display: none; }}
  </style>
</head>
<body>

  <!-- Ambient Light Orbs -->
  <div class="orb orb-1"></div>
  <div class="orb orb-2"></div>
  <div class="orb orb-3"></div>

  <!-- App Wrapper -->
  <div class="app-wrap">

    <!-- Navbar -->
    <header class="navbar">
      <div class="logo-area" onclick="showHome()">
        <div class="logo-badge" id="appLogoBadge">🩺</div>
        <div class="logo-text">
          <h1 id="appTitle">MEDICUS ED8</h1>
          <p id="appSubtitle">Medical MCQ Mastery Platform</p>
        </div>
      </div>

      <!-- Platform Switcher Tabs -->
      <div class="platform-switcher">
        <button class="platform-btn active" id="btnPlatformMarrow" onclick="switchPlatform('marrow')">
          <span class="p-icon">🩺</span>
          <span class="p-name">Marrow <span class="p-badge">ED8</span></span>
          <span class="p-count">16,040 Qs</span>
        </button>
        <button class="platform-btn" id="btnPlatformPrep" onclick="switchPlatform('prep')">
          <span class="p-icon">⚡</span>
          <span class="p-name">PrepLadder <span class="p-badge">VX</span></span>
          <span class="p-count">17,918 Qs</span>
        </button>
      </div>

      <div class="nav-actions">
        <span class="badge-pill emerald" id="datasetStatusBadge">
          <span style="display:inline-block; width:6px; height:6px; background:#10b981; border-radius:50%"></span>
          16,040 MCQs Active
        </span>
        <button class="btn btn-glass btn-icon" onclick="toggleBookmarkedQuiz()" title="Review Saved / Starred Questions">
          ⭐
        </button>
      </div>
    </header>

    <!-- 1. HOME VIEW -->
    <main id="homeView" class="home-view">
      
      <!-- Hero Banner -->
      <section class="hero-banner">
        <div class="hero-content">
          <div class="hero-tag" id="heroTag">✨ Marrow Edition 8 • 16,040 Authentic MCQs with IBQ</div>
          <h2 class="hero-title" id="heroTitle">Prepare for NEET-PG, INI-CET & USMLE with Authentic Marrow ED8 MCQs & Clinical Images</h2>
          <p class="hero-desc" id="heroDesc">
            Practice high-yield clinical vignettes, radiology scans, surgical instruments, histological slides, and detailed rationales extracted directly across all 19 standard medical review specialties.
          </p>
          
          <!-- Stats Ribbon -->
          <div class="stats-ribbon">
            <div class="stat-card">
              <div class="stat-val" id="statSubjects">19</div>
              <div class="stat-lbl">Core Specialties</div>
            </div>
            <div class="stat-card">
              <div class="stat-val" id="statQuestions">16,040 <span>Total</span></div>
              <div class="stat-lbl">Authentic MCQs</div>
            </div>
            <div class="stat-card">
              <div class="stat-val" id="statIBQ" style="color: #f472b6;">2,253 <span>Images</span></div>
              <div class="stat-lbl">Clinical Photographs & X-Rays</div>
            </div>
            <div class="stat-card">
              <div class="stat-val" style="color: var(--emerald);">100%</div>
              <div class="stat-lbl">Verified Rationales</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Action Banners: Grand Mock & IBQ Special -->
      <div class="action-banners-grid">
        <!-- Grand Mock Card -->
        <section class="feature-card grand-mock-card">
          <div class="feature-info">
            <h3 id="mockBannerTitle">🏆 Grand Mock Exam (All 19 Subjects)</h3>
            <p id="mockBannerDesc">Simulate the entrance exam with mixed questions drawn across all 19 clinical disciplines.</p>
          </div>
          <div class="feature-actions">
            <button class="btn btn-primary" onclick="startGrandMock(30)">
              ⚡ 30 Qs Mock
            </button>
            <button class="btn btn-glass" onclick="startGrandMock(60)">
              🎯 60 Qs Full Mock
            </button>
          </div>
        </section>

        <!-- IBQ Image-Based Exam Card -->
        <section class="feature-card ibq-card">
          <div class="feature-info">
            <h3>📷 Image-Based Questions (IBQ) Sprint</h3>
            <p>Practice exclusively image-based MCQs (X-rays, ECGs, surgical instruments, clinical signs).</p>
          </div>
          <div class="feature-actions">
            <button class="btn btn-primary" style="background: linear-gradient(135deg, #ec4899, #8b5cf6);" onclick="startIBQMock(25)">
              🖼️ 25 IBQs
            </button>
            <button class="btn btn-glass" onclick="startIBQMock(50)">
              🔬 50 IBQs
            </button>
          </div>
        </section>
      </div>

      <!-- Controls & Filters -->
      <div class="controls-bar">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" id="subjectSearch" placeholder="Search specialty or topic (e.g. Ophthalmology, Fracture, Anaesthesia)..." oninput="filterSubjects()" />
        </div>

        <div class="config-pills">
          <!-- Mode Selector -->
          <div class="pill-group" id="modeSelector">
            <div class="pill-opt active" onclick="setMode('practice')">💡 Practice Mode</div>
            <div class="pill-opt" onclick="setMode('exam')">⏱️ Exam Mode</div>
          </div>

          <!-- Question Count Selector -->
          <div class="pill-group" id="countSelector">
            <div class="pill-opt" onclick="setQuestionCount(15)">15 Qs</div>
            <div class="pill-opt" onclick="setQuestionCount(30)">30 Qs</div>
            <div class="pill-opt" onclick="setQuestionCount(50)">50 Qs</div>
            <div class="pill-opt active" onclick="setQuestionCount(999)">All Qs</div>
          </div>
        </div>
      </div>

      <!-- Subject Cards Grid -->
      <div class="subject-grid" id="subjectGrid">
        <!-- Rendered dynamically -->
      </div>
    </main>

    <!-- 2. QUIZ VIEW -->
    <main id="quizView" class="quiz-view">
      <!-- Quiz Header -->
      <div class="quiz-header">
        <div class="quiz-info-block">
          <button class="btn btn-glass" onclick="confirmExitQuiz()">
            ← Exit Test
          </button>
          <div class="quiz-subject-badge" id="quizSubjectPill">
            💉 Anaesthesia
          </div>
          <div class="chapter-dropdown-wrap">
            <select class="chapter-dropdown" id="chapterDropdown" onchange="onChapterChange(event)">
              <option value="all">📚 All Chapters</option>
            </select>
          </div>
          <div class="pill-group" id="quizCountPills" style="margin-left: 4px;">
            <div class="pill-opt active" id="pillQuizAll" onclick="setQuizLimit(999)">All</div>
            <div class="pill-opt" id="pillQuiz15" onclick="setQuizLimit(15)">15</div>
            <div class="pill-opt" id="pillQuiz30" onclick="setQuizLimit(30)">30</div>
            <div class="pill-opt" id="pillQuiz50" onclick="setQuizLimit(50)">50</div>
          </div>
          <span class="badge-pill" id="quizModeBadge">Practice Mode</span>
        </div>

        <div class="quiz-info-block">
          <div class="quiz-timer" id="quizTimerDisplay">
            ⏳ <span id="timerText">00:00</span>
          </div>
          <button class="btn btn-glass btn-icon" id="bookmarkBtn" onclick="toggleBookmarkCurrent()" title="Star this question">
            ⭐
          </button>
          <button class="btn btn-primary" onclick="confirmSubmitExam()">
            Finish & Submit
          </button>
        </div>
      </div>

      <!-- Progress Fill -->
      <div class="progress-bar-wrap">
        <div class="progress-fill" id="quizProgressFill"></div>
      </div>

      <!-- Layout: Question + Palette -->
      <div class="question-layout">
        <!-- Main Question Card -->
        <div class="question-card">
          <div class="q-meta">
            <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
              <span class="q-number" id="qNumberText">Question 1 of 30</span>
              <span class="q-chapter" id="qChapterText" style="margin-left: 4px;"></span>
              <select class="chapter-dropdown" id="qChapterDropdown" onchange="onChapterChange(event)" style="font-size:12px; min-width:180px; max-width:340px; padding:4px 28px 4px 10px;">
                <option value="all">📚 All Chapters</option>
              </select>
            </div>
            <div id="qIBQBadgeSlot"></div>
          </div>

          <h3 class="q-text" id="qQuestionText">
            Loading question...
          </h3>

          <!-- Clinical Question Images -->
          <div class="q-images-wrap" id="qImagesContainer" style="display: none;">
            <!-- Rendered clinical images -->
          </div>

          <!-- Options -->
          <div class="options-list" id="optionsList">
            <!-- Options injected here -->
          </div>

          <!-- Explanation (Practice Mode) -->
          <div class="explanation-box" id="explanationBox">
            <div class="exp-hdr">
              <span>🩺 Verified Clinical Rationale</span>
            </div>
            <div class="exp-body" id="explanationText">
              <!-- Explanation text -->
            </div>
            <div class="sol-images-wrap" id="solImagesContainer" style="display: none;">
              <!-- Solution diagrams -->
            </div>
          </div>

          <!-- Question Footer Navigation -->
          <div class="q-footer">
            <div class="q-nav-btns">
              <button class="btn btn-glass" id="prevBtn" onclick="navQuestion(-1)">
                ← Previous
              </button>
              <button class="btn btn-glass" onclick="clearCurrentAnswer()">
                Clear Selection
              </button>
            </div>

            <div class="q-nav-btns">
              <button class="btn btn-primary" id="nextBtn" onclick="navQuestion(1)">
                Next →
              </button>
            </div>
          </div>
        </div>

        <!-- Sidebar: Question Navigator Palette -->
        <aside class="quiz-sidebar">
          <div class="palette-title">
            <span>Question Palette</span>
            <span style="font-size:12px; font-weight:500; color:var(--text-dim);" id="paletteCount">0/30 Answered</span>
          </div>

          <div class="palette-grid" id="paletteGrid">
            <!-- Palette chips -->
          </div>

          <div class="pal-legend">
            <div class="leg-item">
              <div class="leg-dot" style="background:var(--emerald);"></div>
              <span>Answered</span>
            </div>
            <div class="leg-item">
              <div class="leg-dot" style="background:var(--amber);"></div>
              <span>Starred for Review</span>
            </div>
            <div class="leg-item">
              <div class="leg-dot" style="background:#f472b6;"></div>
              <span>Image-Based Question (Dot)</span>
            </div>
            <div class="leg-item">
              <div class="leg-dot" style="background:rgba(255,255,255,0.1);"></div>
              <span>Unvisited / Skipped</span>
            </div>
          </div>
        </aside>
      </div>
    </main>

    <!-- 3. RESULTS VIEW -->
    <main id="resultsView" class="results-view">
      <section class="results-banner">
        <div class="score-circle">
          <div class="score-percent" id="resScorePercent">0%</div>
          <div class="score-label">Accuracy</div>
        </div>

        <h2 class="results-title" id="resTitle">Examination Completed!</h2>
        <p class="results-subtitle" id="resSubtitle">Here is your comprehensive clinical performance breakdown.</p>

        <div class="results-grid">
          <div class="res-metric">
            <div class="res-metric-val cyan" id="resTotal">0</div>
            <div class="res-metric-lbl">Total Questions</div>
          </div>
          <div class="res-metric">
            <div class="res-metric-val green" id="resCorrect">0</div>
            <div class="res-metric-lbl">Correct</div>
          </div>
          <div class="res-metric">
            <div class="res-metric-val red" id="resWrong">0</div>
            <div class="res-metric-lbl">Incorrect</div>
          </div>
          <div class="res-metric">
            <div class="res-metric-val amber" id="resSkipped">0</div>
            <div class="res-metric-lbl">Skipped</div>
          </div>
          <div class="res-metric">
            <div class="res-metric-val" id="resTime">00:00</div>
            <div class="res-metric-lbl">Time Taken</div>
          </div>
        </div>

        <div style="display:flex; justify-content:center; gap:14px; flex-wrap:wrap;">
          <button class="btn btn-primary" onclick="retakeCurrentQuiz()">
            🔄 Retake Test
          </button>
          <button class="btn btn-glass" onclick="filterReviewMistakes()">
            ❌ Review Mistakes Only
          </button>
          <button class="btn btn-glass" onclick="showHome()">
            🏠 Back to Dashboard
          </button>
        </div>
      </section>

      <!-- Solutions Review Header -->
      <div class="review-filter-bar">
        <h3 style="font-family:var(--font-heading); font-size:20px; font-weight:700;">Detailed Question, Image & Rationale Review</h3>
        <div class="pill-group">
          <div class="pill-opt active" id="revAllBtn" onclick="filterReview('all')">All Questions</div>
          <div class="pill-opt" id="revWrongBtn" onclick="filterReview('wrong')">Wrong Only</div>
          <div class="pill-opt" id="revBookmarkedBtn" onclick="filterReview('starred')">Starred Only</div>
          <div class="pill-opt" id="revIbqBtn" onclick="filterReview('ibq')">Images Only</div>
        </div>
      </div>

      <!-- Solutions List -->
      <div class="review-list" id="reviewList">
        <!-- Review cards injected here -->
      </div>
    </main>

  </div>

  <!-- Full-Screen Lightbox / Zoom Modal for Clinical Images -->
  <div class="lightbox-overlay" id="lightboxModal" onclick="closeLightbox()">
    <div class="lightbox-content" onclick="event.stopPropagation()">
      <button class="lightbox-close" onclick="closeLightbox()">✕</button>
      <img id="lightboxImage" src="" alt="Clinical High-Resolution View" />
    </div>
  </div>

  <!-- Confirmation Modal -->
  <div class="modal-overlay" id="confirmModal">
    <div class="modal-card">
      <h3 style="font-family:var(--font-heading); font-size:20px; font-weight:700; color:#fff; margin-bottom:12px;">Submit Examination?</h3>
      <p style="font-size:14px; color:var(--text-muted); margin-bottom:24px;" id="modalMessage">
        Are you sure you want to end this test? All your responses will be evaluated.
      </p>
      <div style="display:flex; justify-content:center; gap:12px;">
        <button class="btn btn-glass" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="confirmSubmitAction()">Submit Now</button>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div class="toast" id="toastBox">
    <span id="toastIcon">⭐</span>
    <span id="toastMsg">Notification message</span>
  </div>

  <!-- Embedded Authentic MCQ Dataset -->
  <script>
    const MARROW_DATA = {marrow_json_str};
    const PREP_DATA = {prep_json_str};

    let currentPlatform = localStorage.getItem('medicus_platform') || 'marrow';
    let ACTIVE_DATA = currentPlatform === 'prep' ? PREP_DATA : MARROW_DATA;

    // App State
    let currentMode = 'practice'; // 'practice' or 'exam'
    let questionLimit = 999;
    let currentQuestions = [];
    let currentIndex = 0;
    let userAnswers = {{}}; // index -> chosen option 'a','b','c','d'
    let bookmarkedIds = new Set(JSON.parse(localStorage.getItem('medicus_bookmarks') || '[]'));
    let timerInterval = null;
    let timerSeconds = 0;
    let testStartTime = 0;
    let reviewFilter = 'all';

    window.addEventListener('DOMContentLoaded', () => {{
      // Sync platform button active states
      const btnMarrow = document.getElementById('btnPlatformMarrow');
      const btnPrep = document.getElementById('btnPlatformPrep');
      if (btnMarrow && btnPrep) {{
        btnMarrow.className = 'platform-btn ' + (currentPlatform === 'marrow' ? 'active' : '');
        btnPrep.className = 'platform-btn ' + (currentPlatform === 'prep' ? 'active prep-active' : '');
      }}
      updatePlatformUI();
      renderSubjectGrid();
      setupKeyboardShortcuts();
    }});

    function switchPlatform(platform) {{
      if (currentPlatform === platform) return;
      localStorage.setItem('medicus_platform', platform);
      location.reload();
    }}

    function updatePlatformUI() {{
      const isPrep = currentPlatform === 'prep';
      const activeObj = isPrep ? PREP_DATA : MARROW_DATA;

      let totalQs = 0;
      let totalIbqs = 0;
      for (const k in activeObj) {{
        const mcqs = activeObj[k].mcqs || [];
        totalQs += mcqs.length;
        totalIbqs += activeObj[k].ibq_count || 0;
      }}

      const appLogoBadge = document.getElementById('appLogoBadge');
      if (appLogoBadge) appLogoBadge.innerText = isPrep ? '⚡' : '🩺';

      const appTitle = document.getElementById('appTitle');
      if (appTitle) appTitle.innerText = isPrep ? 'PREPLADDER VX' : 'MEDICUS ED8';

      const appSubtitle = document.getElementById('appSubtitle');
      if (appSubtitle) appSubtitle.innerText = isPrep ? 'PrepLadder Version X QBank' : 'Marrow Medical MCQ Platform';

      const heroTag = document.getElementById('heroTag');
      if (heroTag) heroTag.innerText = isPrep ? `⚡ PrepLadder Version X • ${{totalQs.toLocaleString()}} Authentic MCQs with IBQ` : `✨ Marrow Edition 8 • ${{totalQs.toLocaleString()}} Authentic MCQs with IBQ`;

      const heroTitle = document.getElementById('heroTitle');
      if (heroTitle) heroTitle.innerText = isPrep ? 'Ace NEET-PG & INI-CET with PrepLadder Version X QBank & Clinical Images' : 'Prepare for NEET-PG, INI-CET & USMLE with Authentic Marrow ED8 MCQs & Clinical Images';

      const statusBadge = document.getElementById('datasetStatusBadge');
      if (statusBadge) {{
        statusBadge.innerHTML = `<span style="display:inline-block; width:6px; height:6px; background:${{isPrep ? '#f59e0b' : '#10b981'}}; border-radius:50%"></span> ${{totalQs.toLocaleString()}} MCQs Active`;
      }}

      const statSubjs = document.getElementById('statSubjects');
      if (statSubjs) statSubjs.innerText = Object.keys(activeObj).length;

      const statQuestions = document.getElementById('statQuestions');
      if (statQuestions) statQuestions.innerHTML = `${{totalQs.toLocaleString()}} <span>Total</span>`;

      const statIBQ = document.getElementById('statIBQ');
      if (statIBQ) statIBQ.innerHTML = `${{totalIbqs.toLocaleString()}} <span>Images</span>`;
    }}

    function renderSubjectGrid() {{
      const grid = document.getElementById('subjectGrid');
      const term = (document.getElementById('subjectSearch').value || '').toLowerCase().trim();
      grid.innerHTML = '';

      for (const [name, info] of Object.entries(ACTIVE_DATA)) {{
        if (term && !name.toLowerCase().includes(term) && !(info.desc || '').toLowerCase().includes(term)) {{
          continue;
        }}

        const card = document.createElement('div');
        card.className = 'subject-card';
        card.style.setProperty('--card-grad', info.grad);
        card.onclick = () => startSubjectQuiz(name);

        const ibqBadge = info.ibq_count ? `<span class="subj-meta-badge ibq">📷 ${{info.ibq_count}} IBQs</span>` : '';
        const mcqsList = info.mcqs || [];
        const chaptersCount = info.chapters_count || new Set(mcqsList.map(q => q.chapter || q.chapter_num)).size;

        card.innerHTML = `
          <div>
            <div class="subj-header">
              <div class="subj-icon">${{info.icon}}</div>
              <div class="subj-meta-badges">
                <span class="subj-meta-badge">${{chaptersCount}} Chapters</span>
                ${{ibqBadge}}
              </div>
            </div>
            <h3 class="subj-title">${{name}}</h3>
            <p class="subj-desc">${{info.desc}}</p>
          </div>
          <div class="subj-footer">
            <div class="subj-stat">
              <span>${{mcqsList.length}}</span> MCQs
            </div>
            <button class="subj-start-btn">Start Test →</button>
          </div>
        `;
        grid.appendChild(card);
      }}
    }}

    function filterSubjects() {{
      renderSubjectGrid();
    }}

    function setMode(mode) {{
      currentMode = mode;
      document.querySelectorAll('#modeSelector .pill-opt').forEach(el => el.classList.remove('active'));
      event.target.classList.add('active');
    }}

    function setQuestionCount(count) {{
      questionLimit = count;
      document.querySelectorAll('#countSelector .pill-opt').forEach(el => el.classList.remove('active'));
      event.target.classList.add('active');
      syncQuizPills(count);
    }}

    function setQuizLimit(count) {{
      questionLimit = count;
      syncQuizPills(count);
      syncHomePills(count);
      const headerDD = document.getElementById('chapterDropdown');
      const val = headerDD ? headerDD.value : 'all';
      applyChapterFilter(val);
      currentIndex = 0;
      userAnswers = {{}};
      renderPalette();
      loadQuestion(0);
      showToast(`Question count set to ${{count === 999 ? 'All' : count}} (${{currentQuestions.length}} Qs loaded)`, '⚡');
    }}

    function syncQuizPills(count) {{
      document.querySelectorAll('#quizCountPills .pill-opt').forEach(el => el.classList.remove('active'));
      if (count === 999) {{
        const p = document.getElementById('pillQuizAll');
        if (p) p.classList.add('active');
      }} else {{
        const p = document.getElementById(`pillQuiz${{count}}`);
        if (p) p.classList.add('active');
      }}
    }}

    function syncHomePills(count) {{
      document.querySelectorAll('#countSelector .pill-opt').forEach(el => el.classList.remove('active'));
      const homePills = document.querySelectorAll('#countSelector .pill-opt');
      if (count === 15 && homePills[0]) homePills[0].classList.add('active');
      else if (count === 30 && homePills[1]) homePills[1].classList.add('active');
      else if (count === 50 && homePills[2]) homePills[2].classList.add('active');
      else if (count === 999 && homePills[3]) homePills[3].classList.add('active');
    }}

    let currentSubjectName = '';
    let currentSubjectPool = [];

    function startSubjectQuiz(subjectName) {{
      const subj = ACTIVE_DATA[subjectName];
      if (!subj || !subj.mcqs || subj.mcqs.length === 0) {{
        showToast('No questions available for this subject', '⚠️');
        return;
      }}

      currentSubjectName = subjectName;
      currentSubjectPool = [...subj.mcqs];

      // Build chapter options
      const chapters = {{}};
      subj.mcqs.forEach(q => {{
        const chKey = q.chapter_num || 0;
        const chName = q.chapter || 'General';
        if (!chapters[chKey]) chapters[chKey] = {{ name: chName, count: 0 }};
        chapters[chKey].count++;
      }});
      const sortedChs = Object.keys(chapters).map(Number).sort((a,b) => a-b);

      // Populate both dropdowns
      const dropdowns = [
        document.getElementById('chapterDropdown'),
        document.getElementById('qChapterDropdown')
      ];

      dropdowns.forEach(dd => {{
        dd.innerHTML = '';
        const allOpt = document.createElement('option');
        allOpt.value = 'all';
        allOpt.textContent = `📚 All Chapters (${{subj.mcqs.length}} Qs)`;
        dd.appendChild(allOpt);

        sortedChs.forEach(chNum => {{
          const opt = document.createElement('option');
          opt.value = chNum;
          const ch = chapters[chNum];
          const label = ch.name.length > 40 ? ch.name.substring(0, 38) + '...' : ch.name;
          opt.textContent = `Ch ${{chNum}}: ${{label}} (${{ch.count}} Qs)`;
          dd.appendChild(opt);
        }});
        dd.style.display = 'inline-block';
      }});

      const qTxt = document.getElementById('qChapterText');
      if (qTxt) qTxt.style.display = 'none';
      const pills = document.getElementById('quizCountPills');
      if (pills) pills.style.display = 'flex';

      applyChapterFilter('all');
      initQuizUI(subjectName, `${{subj.icon}} ${{subjectName}}`);
    }}

    function onChapterChange(e) {{
      const headerDD = document.getElementById('chapterDropdown');
      const questionDD = document.getElementById('qChapterDropdown');
      let val = 'all';
      if (e && e.target) {{
        val = e.target.value;
      }} else if (typeof e === 'string' || typeof e === 'number') {{
        val = String(e);
      }} else if (questionDD) {{
        val = questionDD.value;
      }} else if (headerDD) {{
        val = headerDD.value;
      }}

      if (headerDD) headerDD.value = val;
      if (questionDD) questionDD.value = val;

      applyChapterFilter(val);
      currentIndex = 0;
      userAnswers = {{}};
      renderPalette();
      loadQuestion(0);
      showToast(val === 'all' ? `All chapters loaded (${{currentQuestions.length}} Qs)` : `Chapter loaded (${{currentQuestions.length}} Qs)`, '📖');
    }}

    function applyChapterFilter(chapterVal) {{
      let pool;
      if (chapterVal === 'all') {{
        pool = [...currentSubjectPool];
        if (questionLimit !== 999) {{
          shuffleArray(pool);
          pool = pool.slice(0, Math.min(questionLimit, pool.length));
        }}
        currentQuestions = pool;
      }} else {{
        const chNum = parseInt(chapterVal);
        pool = currentSubjectPool.filter(q => q.chapter_num === chNum);
        pool.sort((a, b) => (a.q_num || 0) - (b.q_num || 0));
        if (questionLimit !== 999) {{
          pool = pool.slice(0, Math.min(questionLimit, pool.length));
        }}
        currentQuestions = pool;
      }}
    }}

    function hideChapterDropdowns() {{
      const headerDD = document.getElementById('chapterDropdown');
      const questionDD = document.getElementById('qChapterDropdown');
      const qTxt = document.getElementById('qChapterText');
      const pills = document.getElementById('quizCountPills');
      if (headerDD) headerDD.style.display = 'none';
      if (questionDD) questionDD.style.display = 'none';
      if (qTxt) qTxt.style.display = 'inline';
      if (pills) pills.style.display = 'none';
    }}

    function startGrandMock(count) {{
      let grandPool = [];
      for (const [name, info] of Object.entries(ACTIVE_DATA)) {{
        if (info.mcqs && info.mcqs.length > 0) {{
          grandPool.push(...info.mcqs);
        }}
      }}
      shuffleArray(grandPool);
      currentQuestions = grandPool.slice(0, Math.min(count, grandPool.length));
      hideChapterDropdowns();
      initQuizUI('Grand Mock Exam', '🏆 Grand Mixed Mock Test');
    }}

    function startIBQMock(count) {{
      let ibqPool = [];
      for (const [name, info] of Object.entries(ACTIVE_DATA)) {{
        for (const q of info.mcqs) {{
          if (q.images && q.images.length > 0) {{
            ibqPool.push(q);
          }}
        }}
      }}

      if (ibqPool.length === 0) {{
        showToast('No image-based questions found in current dataset', '⚠️');
        return;
      }}

      shuffleArray(ibqPool);
      currentQuestions = ibqPool.slice(0, Math.min(count, ibqPool.length));
      hideChapterDropdowns();
      initQuizUI('IBQ Sprint', '📷 Clinical Images & Radiology Sprint');
    }}

    function toggleBookmarkedQuiz() {{
      let bookmarkedPool = [];
      for (const [name, info] of Object.entries(ACTIVE_DATA)) {{
        for (const q of info.mcqs) {{
          if (bookmarkedIds.has(q.id)) {{
            bookmarkedPool.push(q);
          }}
        }}
      }}

      if (bookmarkedPool.length === 0) {{
        showToast('No questions bookmarked yet! Click ⭐ on any question to save.', '⭐');
        return;
      }}

      currentQuestions = bookmarkedPool;
      hideChapterDropdowns();
      initQuizUI('Starred Questions', '⭐ Starred Questions Review');
    }}

    function initQuizUI(title, pillText) {{
      currentIndex = 0;
      userAnswers = {{}};
      testStartTime = Date.now();

      document.getElementById('quizSubjectPill').innerText = pillText;
      document.getElementById('quizModeBadge').innerText = currentMode === 'practice' ? '💡 Practice Mode' : '⏱️ Exam Mode';

      document.getElementById('homeView').style.display = 'none';
      document.getElementById('resultsView').style.display = 'none';
      document.getElementById('quizView').style.display = 'block';

      startTimer();
      renderPalette();
      loadQuestion(0);
    }}

    function loadQuestion(idx) {{
      currentIndex = idx;
      const q = currentQuestions[idx];
      if (!q) return;

      document.getElementById('qNumberText').innerText = `Question ${{idx + 1}} of ${{currentQuestions.length}}`;
      const chEl = document.getElementById('qChapterText');
      if (chEl) chEl.innerText = q.chapter ? `Chapter: ${{q.chapter}}` : (q.subject || '');
      document.getElementById('qQuestionText').innerText = q.question;

      // IBQ Badge
      const ibqBadgeSlot = document.getElementById('qIBQBadgeSlot');
      if (q.images && q.images.length > 0) {{
        ibqBadgeSlot.innerHTML = `<span class="q-ibq-tag">📷 Image-Based Question (${{q.images.length}} Image${{q.images.length > 1 ? 's' : ''}})</span>`;
      }} else {{
        ibqBadgeSlot.innerHTML = '';
      }}

      // Render Question Images
      const imgContainer = document.getElementById('qImagesContainer');
      if (q.images && q.images.length > 0) {{
        imgContainer.style.display = 'flex';
        imgContainer.innerHTML = '';
        q.images.forEach((imgSrc, i) => {{
          const card = document.createElement('div');
          card.className = 'clinical-img-card';
          card.onclick = () => openLightbox(imgSrc);
          card.innerHTML = `
            <img src="${{imgSrc}}" alt="Clinical Image for ${{q.id}}" loading="lazy" />
            <div class="img-zoom-hint">🔍 Click to zoom</div>
          `;
          imgContainer.appendChild(card);
        }});
      }} else {{
        imgContainer.style.display = 'none';
        imgContainer.innerHTML = '';
      }}

      // Progress bar
      const pct = ((idx + 1) / currentQuestions.length) * 100;
      document.getElementById('quizProgressFill').style.width = `${{pct}}%`;

      // Bookmark button
      const bmBtn = document.getElementById('bookmarkBtn');
      bmBtn.innerHTML = bookmarkedIds.has(q.id) ? '★' : '☆';
      bmBtn.style.color = bookmarkedIds.has(q.id) ? 'var(--amber)' : 'inherit';

      // Render Options
      const optList = document.getElementById('optionsList');
      optList.innerHTML = '';

      const userAns = userAnswers[idx];
      const isAnswered = userAns !== undefined;
      const isPractice = currentMode === 'practice';

      const optKeys = ['a', 'b', 'c', 'd'];
      for (const k of optKeys) {{
        const optText = q.options ? (q.options[k] || q.options[k.toUpperCase()]) : null;
        if (!optText) continue;

        const optDiv = document.createElement('div');
        optDiv.className = 'option-item';

        if (isPractice && isAnswered) {{
          optDiv.classList.add('locked');
          if (k === (q.answer || '').toLowerCase()) {{
            optDiv.classList.add('correct');
          }} else if (k === userAns) {{
            optDiv.classList.add('wrong');
          }}
        }} else if (userAns === k) {{
          optDiv.classList.add('selected');
        }}

        optDiv.onclick = () => selectOption(k);

        optDiv.innerHTML = `
          <div class="opt-key">${{k.toUpperCase()}}</div>
          <div class="opt-label">${{optText}}</div>
        `;
        optList.appendChild(optDiv);
      }}

      // Explanation Box
      const expBox = document.getElementById('explanationBox');
      const solImgWrap = document.getElementById('solImagesContainer');
      if (isPractice && isAnswered) {{
        expBox.style.display = 'block';
        document.getElementById('explanationText').innerText = q.explanation || 'No detailed rationale available for this question.';
        
        if (q.solution_images && q.solution_images.length > 0) {{
          solImgWrap.style.display = 'flex';
          solImgWrap.innerHTML = '<div style="width:100%; font-size:12px; font-weight:700; color:var(--cyan); margin-bottom:8px;">🖼️ Clinical Diagram & Reference:</div>';
          q.solution_images.forEach(sImg => {{
            const sc = document.createElement('div');
            sc.className = 'sol-img-card';
            sc.onclick = () => openLightbox(sImg);
            sc.innerHTML = `<img src="${{sImg}}" alt="Solution diagram" loading="lazy" />`;
            solImgWrap.appendChild(sc);
          }});
        }} else {{
          solImgWrap.style.display = 'none';
          solImgWrap.innerHTML = '';
        }}
      }} else {{
        expBox.style.display = 'none';
        solImgWrap.style.display = 'none';
      }}

      // Nav buttons
      document.getElementById('prevBtn').disabled = idx === 0;
      document.getElementById('nextBtn').innerText = idx === currentQuestions.length - 1 ? 'Finish →' : 'Next →';

      updatePaletteItem(idx);
    }}

    function selectOption(key) {{
      const q = currentQuestions[currentIndex];
      if (currentMode === 'practice' && userAnswers[currentIndex] !== undefined) {{
        return;
      }}

      userAnswers[currentIndex] = key;
      loadQuestion(currentIndex);
      updatePaletteCount();
    }}

    function clearCurrentAnswer() {{
      delete userAnswers[currentIndex];
      loadQuestion(currentIndex);
      updatePaletteCount();
    }}

    function navQuestion(delta) {{
      const target = currentIndex + delta;
      if (target >= 0 && target < currentQuestions.length) {{
        loadQuestion(target);
      }} else if (target >= currentQuestions.length) {{
        confirmSubmitExam();
      }}
    }}

    function renderPalette() {{
      const grid = document.getElementById('paletteGrid');
      grid.innerHTML = '';

      currentQuestions.forEach((q, i) => {{
        const btn = document.createElement('button');
        btn.className = 'pal-btn';
        btn.id = `palBtn-${{i}}`;
        btn.innerText = i + 1;
        if (q.images && q.images.length > 0) {{
          btn.classList.add('has-img');
        }}
        btn.onclick = () => loadQuestion(i);
        grid.appendChild(btn);
      }});

      updatePaletteCount();
    }}

    function updatePaletteItem(idx) {{
      document.querySelectorAll('.pal-btn').forEach((b, i) => {{
        b.classList.remove('current');
        if (i === idx) b.classList.add('current');

        b.classList.remove('answered');
        if (userAnswers[i] !== undefined) {{
          b.classList.add('answered');
        }}

        b.classList.remove('flagged');
        const q = currentQuestions[i];
        if (q && bookmarkedIds.has(q.id)) {{
          b.classList.add('flagged');
        }}
      }});
    }}

    function updatePaletteCount() {{
      const answered = Object.keys(userAnswers).length;
      document.getElementById('paletteCount').innerText = `${{answered}}/${{currentQuestions.length}} Answered`;
    }}

    function toggleBookmarkCurrent() {{
      const q = currentQuestions[currentIndex];
      if (!q) return;

      if (bookmarkedIds.has(q.id)) {{
        bookmarkedIds.delete(q.id);
        showToast('Question unstarred', '☆');
      }} else {{
        bookmarkedIds.add(q.id);
        showToast('Question starred for review!', '⭐');
      }}

      localStorage.setItem('medicus_bookmarks', JSON.stringify(Array.from(bookmarkedIds)));
      loadQuestion(currentIndex);
    }}

    // Lightbox / Image Zoom
    function openLightbox(imgSrc) {{
      const modal = document.getElementById('lightboxModal');
      const img = document.getElementById('lightboxImage');
      img.src = imgSrc;
      modal.style.display = 'flex';
    }}

    function closeLightbox() {{
      document.getElementById('lightboxModal').style.display = 'none';
    }}

    // Timer
    function startTimer() {{
      clearInterval(timerInterval);
      timerSeconds = 0;
      timerInterval = setInterval(() => {{
        timerSeconds++;
        const mins = String(Math.floor(timerSeconds / 60)).padStart(2, '0');
        const secs = String(timerSeconds % 60).padStart(2, '0');
        document.getElementById('timerText').innerText = `${{mins}}:${{secs}}`;
      }}, 1000);
    }}

    function stopTimer() {{
      clearInterval(timerInterval);
    }}

    // Modal
    function confirmSubmitExam() {{
      const answered = Object.keys(userAnswers).length;
      const total = currentQuestions.length;
      document.getElementById('modalMessage').innerText = `You have answered ${{answered}} out of ${{total}} questions. Do you want to submit and view your score?`;
      document.getElementById('confirmModal').style.display = 'flex';
    }}

    function closeModal() {{
      document.getElementById('confirmModal').style.display = 'none';
    }}

    function confirmSubmitAction() {{
      closeModal();
      submitExam();
    }}

    function confirmExitQuiz() {{
      stopTimer();
      showHome();
    }}

    function submitExam() {{
      stopTimer();
      evaluateResults();
    }}

    function evaluateResults() {{
      let correct = 0;
      let wrong = 0;
      let skipped = 0;

      currentQuestions.forEach((q, i) => {{
        const ans = userAnswers[i];
        if (!ans) {{
          skipped++;
        }} else if (ans.toLowerCase() === (q.answer || '').toLowerCase()) {{
          correct++;
        }} else {{
          wrong++;
        }}
      }});

      const total = currentQuestions.length;
      const pct = total > 0 ? Math.round((correct / total) * 100) : 0;

      document.getElementById('resScorePercent').innerText = `${{pct}}%`;
      document.getElementById('resTotal').innerText = total;
      document.getElementById('resCorrect').innerText = correct;
      document.getElementById('resWrong').innerText = wrong;
      document.getElementById('resSkipped').innerText = skipped;

      const mins = String(Math.floor(timerSeconds / 60)).padStart(2, '0');
      const secs = String(timerSeconds % 60).padStart(2, '0');
      document.getElementById('resTime').innerText = `${{mins}}:${{secs}}`;

      if (pct >= 80) {{
        document.getElementById('resTitle').innerText = 'Outstanding Performance! 🌟';
        document.getElementById('resSubtitle').innerText = 'Exceptional clinical mastery! You are performing at rank-1 competitive level.';
      }} else if (pct >= 60) {{
        document.getElementById('resTitle').innerText = 'Solid Performance! 🩺';
        document.getElementById('resSubtitle').innerText = 'Good conceptual grasp. Review the marked and incorrect rationales below.';
      }} else {{
        document.getElementById('resTitle').innerText = 'Keep Pushing! 📚';
        document.getElementById('resSubtitle').innerText = 'Focus on the detailed rationales below to solidify high-yield concepts.';
      }}

      renderReviewList('all');

      document.getElementById('quizView').style.display = 'none';
      document.getElementById('resultsView').style.display = 'block';
    }}

    function renderReviewList(filter) {{
      reviewFilter = filter;
      const list = document.getElementById('reviewList');
      list.innerHTML = '';

      document.querySelectorAll('.review-filter-bar .pill-opt').forEach(el => el.classList.remove('active'));
      if (filter === 'all') document.getElementById('revAllBtn').classList.add('active');
      if (filter === 'wrong') document.getElementById('revWrongBtn').classList.add('active');
      if (filter === 'starred') document.getElementById('revBookmarkedBtn').classList.add('active');
      if (filter === 'ibq') document.getElementById('revIbqBtn').classList.add('active');

      currentQuestions.forEach((q, i) => {{
        const userAns = userAnswers[i];
        const isCorrect = userAns && userAns.toLowerCase() === (q.answer || '').toLowerCase();
        const isWrong = userAns && !isCorrect;
        const isSkipped = !userAns;
        const hasImgs = q.images && q.images.length > 0;

        if (filter === 'wrong' && !isWrong) return;
        if (filter === 'starred' && !bookmarkedIds.has(q.id)) return;
        if (filter === 'ibq' && !hasImgs) return;

        const card = document.createElement('div');
        card.className = 'review-item';

        let badgeHtml = '';
        if (isCorrect) {{
          badgeHtml = `<span class="rev-badge correct">✓ Correct</span>`;
        }} else if (isWrong) {{
          badgeHtml = `<span class="rev-badge wrong">✗ Incorrect</span>`;
        }} else {{
          badgeHtml = `<span class="rev-badge unanswered">○ Unattempted</span>`;
        }}

        // Question Images HTML
        let qImgsHtml = '';
        if (hasImgs) {{
          qImgsHtml = '<div class="q-images-wrap" style="justify-content:flex-start; margin-bottom:18px;">';
          q.images.forEach(imgSrc => {{
            qImgsHtml += `
              <div class="clinical-img-card" style="max-width:320px;" onclick="openLightbox('${{imgSrc}}')">
                <img src="${{imgSrc}}" alt="Question image" loading="lazy" />
                <div class="img-zoom-hint">🔍 Zoom</div>
              </div>
            `;
          }});
          qImgsHtml += '</div>';
        }}

        // Solution Diagrams HTML
        let solImgsHtml = '';
        if (q.solution_images && q.solution_images.length > 0) {{
          solImgsHtml = '<div class="sol-images-wrap" style="margin-top:12px;">';
          q.solution_images.forEach(sImg => {{
            solImgsHtml += `
              <div class="sol-img-card" onclick="openLightbox('${{sImg}}')">
                <img src="${{sImg}}" alt="Solution diagram" loading="lazy" />
              </div>
            `;
          }});
          solImgsHtml += '</div>';
        }}

        let optionsHtml = '';
        const optKeys = ['a', 'b', 'c', 'd'];
        for (const k of optKeys) {{
          const optText = q.options ? (q.options[k] || q.options[k.toUpperCase()]) : null;
          if (!optText) continue;
          let optClass = 'option-item locked';
          if (k === (q.answer || '').toLowerCase()) {{
            optClass += ' correct';
          }} else if (k === userAns) {{
            optClass += ' wrong';
          }}

          optionsHtml += `
            <div class="${{optClass}}">
              <div class="opt-key">${{k.toUpperCase()}}</div>
              <div class="opt-label">${{optText}}</div>
            </div>
          `;
        }}

        card.innerHTML = `
          <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
            <div>
              ${{badgeHtml}} 
              ${{hasImgs ? '<span class="q-ibq-tag" style="margin-left:8px;">📷 IBQ</span>' : ''}}
              <span style="font-size:12px; color:var(--text-dim); margin-left:8px;">Q${{i + 1}} • ${{q.chapter || q.subject || ''}}</span>
            </div>
            <button class="btn btn-glass btn-icon" onclick="toggleReviewBookmark('${{q.id}}', this)">
              ${{bookmarkedIds.has(q.id) ? '★' : '☆'}}
            </button>
          </div>
          <h4 style="font-size:16px; font-weight:600; color:#fff; line-height:1.5; margin-bottom:14px;">${{q.question}}</h4>
          ${{qImgsHtml}}
          <div class="options-list" style="margin-bottom:18px;">
            ${{optionsHtml}}
          </div>
          <div class="explanation-box" style="display:block; margin-top:0;">
            <div class="exp-hdr">🩺 Verified Rationale:</div>
            <div class="exp-body">${{q.explanation || 'No detailed rationale available.'}}</div>
            ${{solImgsHtml}}
          </div>
        `;
        list.appendChild(card);
      }});

      if (list.children.length === 0) {{
        list.innerHTML = `<div style="text-align:center; padding:40px; color:var(--text-dim); font-size:14px;">No questions match this filter.</div>`;
      }}
    }}

    function filterReview(type) {{
      renderReviewList(type);
    }}

    function filterReviewMistakes() {{
      renderReviewList('wrong');
    }}

    function toggleReviewBookmark(qid, btn) {{
      if (bookmarkedIds.has(qid)) {{
        bookmarkedIds.delete(qid);
        btn.innerHTML = '☆';
        showToast('Removed from starred', '☆');
      }} else {{
        bookmarkedIds.add(qid);
        btn.innerHTML = '★';
        showToast('Saved to starred!', '⭐');
      }}
      localStorage.setItem('medicus_bookmarks', JSON.stringify(Array.from(bookmarkedIds)));
    }}

    function retakeCurrentQuiz() {{
      userAnswers = {{}};
      initQuizUI(document.getElementById('quizSubjectPill').innerText, document.getElementById('quizSubjectPill').innerText);
    }}

    function showHome() {{
      document.getElementById('quizView').style.display = 'none';
      document.getElementById('resultsView').style.display = 'none';
      document.getElementById('homeView').style.display = 'block';
    }}

    function showToast(msg, icon = '⭐') {{
      const box = document.getElementById('toastBox');
      document.getElementById('toastMsg').innerText = msg;
      document.getElementById('toastIcon').innerText = icon;
      box.classList.add('show');
      setTimeout(() => box.classList.remove('show'), 2500);
    }}

    function setupKeyboardShortcuts() {{
      window.addEventListener('keydown', (e) => {{
        if (e.key === 'Escape') closeLightbox();
        if (document.getElementById('quizView').style.display === 'block') {{
          if (['1', 'a', 'A'].includes(e.key)) selectOption('a');
          if (['2', 'b', 'B'].includes(e.key)) selectOption('b');
          if (['3', 'c', 'C'].includes(e.key)) selectOption('c');
          if (['4', 'd', 'D'].includes(e.key)) selectOption('d');
          if (e.key === 'ArrowRight' || e.key === 'n' || e.key === 'N') navQuestion(1);
          if (e.key === 'ArrowLeft' || e.key === 'p' || e.key === 'P') navQuestion(-1);
          if (e.key === 'b' || e.key === 'B') toggleBookmarkCurrent();
        }}
      }});
    }}

    function shuffleArray(arr) {{
      for (let i = arr.length - 1; i > 0; i--) {{
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
      }}
    }}
  </script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Successfully generated index.html with Full Image Support ({os.path.getsize('index.html')} bytes)")

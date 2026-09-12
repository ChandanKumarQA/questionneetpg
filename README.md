# NEET PG Medical MCQ Portal & Question Bank

Comprehensive NEET PG / NEXT preparation repository featuring interactive question bank portal, image-based clinical questions (IBQs), and extraction utilities.

## Features
- **Dual Platform Support**: Comprehensive coverage across **Marrow ED8** and **PrepLadder VX**.
- **19 Medical Specialties**: Complete coverage from Anatomy, Physiology, Pathology to Medicine, Surgery, and Radiology.
- **Interactive MCQ Portal (`index.html`)**: Rich UI with subject filtering, instant search, clinical explanations, and high-resolution image viewer.
- **Automated Extraction Scripts**:
  - `build_index_html.py`: Generates the self-contained interactive web portal.
  - `extract_all_with_images.py`: Extracts MCQs, explanations, and embedded images from PDFs.
  - `extract_all_prep.py`: Extraction pipeline for PrepLadder question banks.
  - `reassign_prep_images.py`: Image mapping and association tool.

## Structure
- `index.html`: Standalone interactive web portal.
- `mcq_data.json`: Structured Marrow ED8 MCQs and clinical explanations.
- `prep_mcq_data.json`: Structured PrepLadder VX MCQs.
- `images/`: High-resolution extracted clinical and radiological diagrams.
- `maro/`: Marrow ED8 question bank PDFs.
- `prep/`: PrepLadder Version X question bank PDFs.

## How to Run
Simply open `index.html` in any modern web browser or host on GitHub Pages / local HTTP server:
```bash
python3 -m http.server 8000
```
Then visit `http://localhost:8000` in your browser.

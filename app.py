import html
import io
import streamlit as st
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

from plagiarism import compare_documents
from pdf_reader import extract_text
from database import load_reference_documents

st.set_page_config(page_title="CopyCheck AI", page_icon="🔎", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 48%, #f5eaff 100%);
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Gradient project header */
.hero {
    padding: 30px;
    border-radius: 20px;
    background: linear-gradient(120deg, #172554, #3730a3, #6d28d9);
    color: white;
    margin-bottom: 1rem;
    box-shadow: 0 8px 25px rgba(55, 48, 163, 0.22);
}
.hero h1 {
    color: white;
    font-size: 2.35rem;
    margin: 0;
    font-weight: 800;
}
.hero p {
    color: #e0e7ff;
    margin: .4rem 0 0 0;
}

/* Information notice */
.notice {
    background: #e0e7ff;
    border: 1px solid #c7d2fe;
    color: #312e81;
    border-radius: 12px;
    padding: 14px 16px;
    margin: 14px 0 20px;
}

/* Dashboard metric cards */
.metric {
    background: linear-gradient(145deg, #ffffff, #f3f0ff);
    border: 1px solid #dcd6ff;
    border-radius: 18px;
    padding: 20px;
    min-height: 110px;
    box-shadow: 0 5px 18px rgba(79, 70, 229, 0.10);
    transition: transform .2s ease, box-shadow .2s ease;
}
.metric:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px rgba(79, 70, 229, 0.18);
}
.metric-label {
    color: #6366a0;
    font-size: .82rem;
    font-weight: 600;
}
.metric-value {
    color: #3730a3;
    font-size: 1.9rem;
    font-weight: 800;
    margin-top: 7px;
}

/* Comparison and result cards */
.section-card {
    background: #ffffff;
    border: 1px solid #ddd6fe;
    border-radius: 15px;
    padding: 18px 20px;
    margin: 12px 0;
    box-shadow: 0 4px 15px rgba(79, 70, 229, 0.08);
}
.match {
    background: #fef3c7;
    color: #92400e;
    padding: 4px 6px;
    border-radius: 5px;
    font-weight: 600;
}
.small-muted {
    color: #64748b;
    font-size: .85rem;
}

/* Navigation tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255, 255, 255, .92);
    border: 1px solid #e0e7ff;
    border-radius: 13px;
    padding: 7px;
    gap: 7px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    color: #3730a3;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: #e0e7ff;
    color: #312e81;
}

/* Buttons */
div.stButton > button[kind="primary"],
.stDownloadButton button {
    background: linear-gradient(120deg, #4338ca, #7c3aed);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    transition: .2s ease;
}
div.stButton > button[kind="primary"]:hover,
.stDownloadButton button:hover {
    background: linear-gradient(120deg, #312e81, #6d28d9);
    color: #ffffff;
    border: none;
    transform: translateY(-1px);
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, .75);
    border: 1px dashed #a5b4fc;
    border-radius: 14px;
    padding: 10px;
}

/* Expanders and tables */
[data-testid="stExpander"] {
    background: rgba(255, 255, 255, .88);
    border: 1px solid #ddd6fe;
    border-radius: 12px;
}
[data-testid="stDataFrame"] {
    border: 1px solid #ddd6fe;
    border-radius: 12px;
    overflow: hidden;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🔎 CopyCheck AI</h1>
  <p>Academic similarity screening using Natural Language Processing</p>
</div>
<div class="notice">
  <b>Educational prototype:</b> similarity scores identify textual overlap; they do not prove plagiarism.
  Review sources, quotations and citations before making a judgment.
</div>
""", unsafe_allow_html=True)

def make_pdf_report(results, mode, uploaded_names, reference_count=0):
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                           topMargin=17*mm, bottomMargin=17*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SmallText", parent=styles["BodyText"], fontSize=8, leading=11))
    styles.add(ParagraphStyle(name="TitleBlue", parent=styles["Title"], textColor=colors.HexColor("#3730a3")))
    story = [
        Paragraph("CopyCheck AI – Similarity Analysis Report", styles["TitleBlue"]),
        Spacer(1, 5*mm),
        Paragraph("Analysis mode: " + html.escape(mode), styles["BodyText"]),
        Paragraph("Uploaded documents: " + html.escape(", ".join(uploaded_names)), styles["BodyText"]),
        Paragraph("Reference documents available: " + str(reference_count), styles["BodyText"]),
        Spacer(1, 5*mm),
    ]
    if results:
        highest = max(r["score"] for r in results)
        average = sum(r["score"] for r in results) / len(results)
        exact_total = sum(len(r["matches"]) for r in results)
        story.append(Paragraph(
            f"<b>Summary:</b> {len(results)} comparisons | Highest similarity: {highest:.1f}% | "
            f"Average similarity: {average:.1f}% | Exact matching sentences: {exact_total}",
            styles["BodyText"]))
        story.append(Spacer(1, 4*mm))
        rows = [["Source document", "Compared with", "Similarity"]]
        for r in results:
            rows.append([
                Paragraph(html.escape(r["source"]), styles["SmallText"]),
                Paragraph(html.escape(r["target"]), styles["SmallText"]),
                f'{r["score"]:.1f}%'
            ])
        table = Table(rows, colWidths=[65*mm, 75*mm, 25*mm], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#3730a3")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#ddd6fe")),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f3f6fb")]),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        story.extend([table, Spacer(1, 5*mm)])
        story.append(Paragraph("Exact matching sentences", styles["Heading2"]))
        any_match = False
        for r in results:
            if r["matches"]:
                any_match = True
                story.append(Paragraph(
                    f"<b>{html.escape(r['source'])}</b> vs <b>{html.escape(r['target'])}</b>",
                    styles["SmallText"]))
                for sentence in r["matches"]:
                    story.append(Paragraph("• " + html.escape(sentence), styles["SmallText"]))
                story.append(Spacer(1, 2*mm))
        if not any_match:
            story.append(Paragraph("No exact matching sentences were detected.", styles["BodyText"]))
    else:
        story.append(Paragraph("No comparisons were available for this analysis.", styles["BodyText"]))
    story.extend([
        Spacer(1, 7*mm),
        Paragraph("<b>Important:</b> Similarity percentages are screening indicators, not proof of plagiarism. "
                  "Common phrases, quotations, references and standard definitions can produce matches. "
                  "Review original sources before making any academic decision.", styles["SmallText"])
    ])
    pdf.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def show_highlighted_matches(matches):
    if not matches:
        st.caption("No exact matching sentences detected. Similar wording may still contribute to the score.")
        return
    st.markdown("**Exact matching sentences**")
    for sentence in matches:
        safe = html.escape(sentence)
        st.markdown(f'<div class="section-card"><span class="match">{safe}</span></div>', unsafe_allow_html=True)

def show_results(results, mode, uploaded_names, reference_count=0):
    if not results:
        st.warning("No comparisons were produced. Check that your files contain selectable text.")
        return
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    highest = max(r["score"] for r in results)
    average = sum(r["score"] for r in results) / len(results)
    exact_total = sum(len(r["matches"]) for r in results)
    c1,c2,c3,c4 = st.columns(4)
    metrics = [
        ("Comparisons", str(len(results))),
        ("Highest similarity", f"{highest:.1f}%"),
        ("Average similarity", f"{average:.1f}%"),
        ("Exact matching sentences", str(exact_total))
    ]
    for col,(label,value) in zip([c1,c2,c3,c4],metrics):
        with col:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)
    st.subheader("Comparison overview")
    frame = pd.DataFrame([{
        "Source document": r["source"],
        "Compared with": r["target"],
        "Similarity (%)": round(r["score"],1),
        "Exact matches": len(r["matches"])
    } for r in results])
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.subheader("Detailed matching results")
    for i,r in enumerate(results, start=1):
        label = f"{i}. {r['source']}  ↔  {r['target']}  |  {r['score']:.1f}%"
        with st.expander(label, expanded=(i == 1)):
            st.progress(min(max(int(round(r["score"])),0),100))
            show_highlighted_matches(r["matches"])
    pdf_bytes = make_pdf_report(results, mode, uploaded_names, reference_count)
    st.download_button(
        "⬇️ Download PDF analysis report",
        data=pdf_bytes,
        file_name="CopyCheck_AI_Analysis_Report.pdf",
        mime="application/pdf",
        type="primary"
    )

tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Compare documents", "🗂️ Reference database", "📊 Dashboard", "ℹ️ About NLP"
])

with tab1:
    st.subheader("Document-to-document comparison")
    st.write("Upload two or more PDF or TXT assignments. Every uploaded pair will be compared.")
    uploads = st.file_uploader("Choose PDF or TXT files", type=["pdf", "txt"], accept_multiple_files=True, key="pair_upload")
    if st.button("Compare uploaded documents", type="primary", disabled=not uploads):
        docs = []
        for f in uploads:
            try:
                text = extract_text(f.name, f.getvalue())
                if text.strip():
                    docs.append({"name": f.name, "text": text})
                else:
                    st.warning(f"No selectable text found in {f.name}. Scanned PDFs need OCR.")
            except Exception as e:
                st.error(f"Could not read {f.name}: {e}")
        if len(docs) < 2:
            st.warning("Please upload at least two readable documents.")
        else:
            from itertools import combinations
            results = [
                compare_documents(a["name"], a["text"], b["name"], b["text"], "Uploaded documents")
                for a,b in combinations(docs,2)
            ]
            st.session_state["pair_results"] = results
            st.session_state["pair_names"] = [d["name"] for d in docs]
    if st.session_state.get("pair_results"):
        show_results(st.session_state["pair_results"], "Document-to-document", st.session_state.get("pair_names", []))

with tab2:
    st.subheader("Document-to-reference database")
    refs = load_reference_documents()
    st.write(f"Reference collection currently contains **{len(refs)}** sample documents.")
    with st.expander("View reference document names"):
        for ref in refs:
            st.write("•", ref["filename"])
    reference_uploads = st.file_uploader("Upload assignment(s) to check against the reference collection", type=["pdf", "txt"], accept_multiple_files=True, key="ref_upload")
    if st.button("Check against reference database", type="primary", disabled=not reference_uploads):
        if not refs:
            st.warning("No reference documents found. Add .txt or text-based .pdf files to the dataset folder.")
        else:
            results = []
            names = []
            for f in reference_uploads:
                try:
                    text = extract_text(f.name, f.getvalue())
                    if not text.strip():
                        st.warning(f"No selectable text found in {f.name}.")
                        continue
                    names.append(f.name)
                    for ref in refs:
                        results.append(compare_documents(f.name, text, ref["filename"], ref["text"], "Reference database"))
                except Exception as e:
                    st.error(f"Could not read {f.name}: {e}")
            st.session_state["reference_results"] = results
            st.session_state["reference_names"] = names
    if st.session_state.get("reference_results"):
        show_results(st.session_state["reference_results"], "Reference database", st.session_state.get("reference_names", []), len(refs))

with tab3:
    st.subheader("Analysis dashboard")
    pair = st.session_state.get("pair_results", [])
    ref_results = st.session_state.get("reference_results", [])
    all_results = pair + ref_results
    if all_results:
        st.write("Summary of analyses performed during this browser session.")
        c1,c2,c3,c4 = st.columns(4)
        total_docs = len(set(st.session_state.get("pair_names", []) + st.session_state.get("reference_names", [])))
        values = [
            ("Total comparisons", str(len(all_results))),
            ("Documents checked", str(total_docs)),
            ("Highest similarity", f"{max(r['score'] for r in all_results):.1f}%"),
            ("Exact matching sentences", str(sum(len(r["matches"]) for r in all_results)))
        ]
        for col,(label,value) in zip([c1,c2,c3,c4],values):
            with col:
                st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)
        df = pd.DataFrame([{"Source":r["source"],"Compared with":r["target"],"Similarity":r["score"]} for r in all_results])
        st.subheader("Similarity by comparison")
        for _, row in df.iterrows():
            st.write(f"**{row['Source']}** compared with **{row['Compared with']}**")
            score = float(row["Similarity"])
            st.progress(min(max(int(round(score)), 0), 100))
            st.caption(f"Similarity: {score:.1f}%")
    else:
        st.info("Run a document comparison or reference database check. Your analysis statistics will appear here.")

with tab4:
    st.subheader("NLP techniques used")
    st.markdown("""
    1. **Text extraction:** reads selectable text from PDF and TXT files.
    2. **Preprocessing:** normalizes case and whitespace.
    3. **Tokenization:** TF-IDF token pattern splits text into word features.
    4. **Stop-word filtering:** common English words are filtered by scikit-learn.
    5. **TF-IDF:** represents documents using term importance.
    6. **Cosine similarity:** measures similarity between document vectors.
    7. **N-gram analysis:** unigram and bigram features capture single words and two-word phrases.
    8. **Sentence matching:** separately identifies exact matching sentences.
    """)
    st.caption("Limitations: this prototype does not search the public internet or commercial plagiarism databases. Paraphrasing may not be detected reliably. Scanned PDFs require OCR.")

st.divider()
st.caption("CopyCheck AI | NLP Mini Project | Similarity scores are indicators for review, not plagiarism verdicts.")

import io
import math
import qrcode
import pandas as pd 
import streamlit as st 
import numpy as np
from matplotlib import pyplot as plt 
from matplotlib.backends.backend_pdf import PdfPages
from pathlib import Path

LIST_EXTENSIONS = ['csv', 'tsv', 'txt']
SEPARATORS = {'comma': ',', 'tab': '\t'}

def generate_pdf(qrcodes, labels, num_per_row=3, rows_per_page=4):
    """Generates the PDF only when triggered."""
    pdf_buffer = io.BytesIO()
    
    with PdfPages(pdf_buffer) as pdf:
        nb_imgs = len(qrcodes)
        imgs_per_page = num_per_row * rows_per_page
        num_pages = math.ceil(nb_imgs / imgs_per_page)
        
        for p in range(num_pages):
            fig, axes = plt.subplots(rows_per_page, num_per_row, figsize=(8.27, 11.69))
            axes = axes.flatten() if isinstance(axes, np.ndarray) else [axes]
            
            for i, ax in enumerate(axes):
                idx = p * imgs_per_page + i
                if idx < nb_imgs:
                    ax.imshow(qrcodes[idx].get_image(), cmap='gray')
                    ax.set_title(labels[idx], fontsize=10)
                ax.axis('off')
                
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)
            
    return pdf_buffer.getvalue()

def main():
    st.set_page_config(page_title="Sample QRcode Generator")

    st.write("## Sample QRcode Generator")
    st.divider()

    st.markdown("""
        This app takes as input a single file with at least one column (the first row should be named `sample_ID`).
When you upload your file, the app will generate QR codes for each sample ID within the input file.

**NOTE:** For CSV files, make sure that the separator is a `comma (,)`, not a `semicolon (;)`.
For TSV files, make sure that the separator is a `tab`.
        """)

    st.divider()

    uploaded_file = st.sidebar.file_uploader(
        "Upload your file with only one column with sample IDs as explained above.", 
        type=LIST_EXTENSIONS, 
        accept_multiple_files=False
    )

    if uploaded_file is not None:
        file_extension = Path(uploaded_file.name).suffix.replace(".", "").lower()

        if file_extension == 'csv':
            sample_data = pd.read_csv(uploaded_file)
        elif file_extension == 'tsv':
            sample_data = pd.read_table(uploaded_file, sep='\t')
        else:
            selected_extension = st.sidebar.selectbox(
                label="Select the right extension",
                options=list(SEPARATORS.keys())
            )
            sample_data = pd.read_table(uploaded_file, sep=SEPARATORS[selected_extension])
        
        if 'sample_ID' in sample_data.columns:
            num_per_row = st.sidebar.select_slider(label="Number of images per row", options=range(1, 31), value=10)
            num_qrcode_per_page = st.sidebar.select_slider(label="Number of images per PDF page", options=range(1, 31), value=12)
            
            tab1, tab2 = st.tabs(["Data Preview", "QR code"])
            
            with tab1:
                st.dataframe(sample_data)
            
            with tab2:
                labels = sample_data['sample_ID'].tolist()
                qrcodes = [qrcode.make(label) for label in labels]
                nb_imgs = len(qrcodes)
                
                if 'pdf_ready' not in st.session_state:
                    st.session_state.pdf_ready = False
                    st.session_state.pdf_data = None
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Prepare PDF for Download"):
                        with st.spinner("Generating PDF... Please wait."):
                            st.session_state.pdf_data = generate_pdf(
                                qrcodes, labels, num_per_row=num_per_row, rows_per_page=num_qrcode_per_page
                            )
                            st.session_state.pdf_ready = True
                with c2:
                    if st.session_state.pdf_ready:
                        st.download_button(
                            label="Download All QR Codes as PDF",
                            data=st.session_state.pdf_data,
                            file_name="Sample_QRCodes.pdf",
                            mime="application/pdf",
                            type="primary", icon="📄"
                        )
                
                st.divider()
                num_rows = nb_imgs // num_per_row if nb_imgs % num_per_row == 0 else 1 + (nb_imgs // num_per_row)
                cols = st.columns(num_per_row)
                
                for i in range(num_per_row):
                    with cols[i]:
                        for j in range(num_rows):
                            idx = j * num_per_row + i
                            if idx < nb_imgs:
                                st.image(qrcodes[idx].get_image(), caption=labels[idx])

        else:
            st.error("There is no column named `sample_ID` in your data file")

if __name__ == '__main__':
    main()
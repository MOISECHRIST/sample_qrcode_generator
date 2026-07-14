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
SEPARATORS = {'comma':',',
              'tab':'\t'}

def plot_qrcode(image, title):
    fig, ax = plt.subplots()
    ax.imshow(image, cmap='grey')
    ax.axis('off')
    ax.set_title(title, fontsize=20)
    return fig

def generate_pdf(qrcodes, labels, num_per_row=3, rows_per_page=4):
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
                    ax.imshow(qrcodes[idx], cmap='gray')
                    ax.set_title(labels[idx], fontsize=12)
                ax.axis('off')
                
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)
            
    return pdf_buffer.getvalue()

def main():
    st.set_page_config(
        page_title="Sample QRcode Generator"
    )

    st.write("## Sample QRcode Generator")
    st.divider()

    st.markdown("""
        This app takes as input a single file with at least one column (the first row should be named `sample_ID`).
When you upload your file, the app will generate QR codes for each sample ID within the input file.

**NOTE:** For CSV files, make sure that the separator is a `comma (,)`, not a `semicolon (;)`.
For TSV files, make sure that the separator is a `tab`.
        """)

    st.divider()

    uploaded_file = st.sidebar.file_uploader("Upload your file with only one column with sample IDs as explained above.", 
                                             type=LIST_EXTENSIONS, 
                                             accept_multiple_files=False)

    if uploaded_file is not None:
        file_extension = Path(uploaded_file.name).suffix.replace(".", "").lower()

        if file_extension == 'csv':
            sample_data = pd.read_csv(uploaded_file)
        elif file_extension == 'tsv':
            sample_data = pd.read_table(uploaded_file, sep='\t')
        else:
            selected_extension = st.sidebar.selectbox(label="Select the right extension",
                                                    options=SEPARATORS.keys())
            sample_data = pd.read_table(uploaded_file, sep=SEPARATORS[selected_extension])
        
        if 'sample_ID' in list(sample_data.columns):
            num_per_row = st.sidebar.select_slider(label="Number of images per row", options=range(1,31), value=10)
            num_qrcode_per_page = st.sidebar.select_slider(label="Number of images per page", options=range(1,31), value=10)
            tab1, tab2 = st.tabs(["Data Preview", "QR code"])
            with tab1:
                st.dataframe(sample_data)
            
            with tab2:
                qrcodes = [qrcode.make(sample_id) for sample_id in sample_data['sample_ID']]
                nb_imgs = len(qrcodes)
                labels = sample_data['sample_ID'].tolist()
                st.download_button(
                    label="Download All QR Codes as PDF",
                    data=generate_pdf(qrcodes, labels, num_per_row=num_per_row, rows_per_page=num_qrcode_per_page),
                    file_name="Sample_QRCodes.pdf",
                    mime="application/pdf",
                    type="primary"
                )
                num_rows = nb_imgs//num_per_row if nb_imgs%num_per_row==0 else 1+nb_imgs//num_per_row
                cols = st.columns(num_per_row)
                for i in range(num_per_row):
                    with cols[i]:
                        for j in range(num_rows):
                            idx = j * num_per_row + i
                            if idx < nb_imgs:
                                label = labels[idx]
                                fig = plot_qrcode(qrcodes[idx], label)
                                st.pyplot(fig)
                                plt.close(fig)

        else:
            st.error("There is no column named `sample_ID` in your data file")


if __name__ == '__main__':
    main()
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from zipfile import ZipFile
from streamlit_pdf_viewer import pdf_viewer

footer = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: white;
    color: black;
    text-align: center;
    font-size: small;
    font-style: italic;
}
a {
    color: blue;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
</style>
<div class="footer">
    By: Daniel Rosehill and GPT-4o (<a href="https://danielrosehill.com" target="_blank">danielrosehill.com</a>)
    <br>
    <a href="https://github.com/danielrosehill/Sustainability-Report-Data-Extractor" target="_blank">
        <img src="https://img.shields.io/badge/GitHub-Repository-blue" alt="GitHub Repository">
    </a>
</div>
"""

# Function to generate a summarized file name based on the original file name
def generate_summarized_filename(original_filename):
    base_name = original_filename.split('.')[0]
    shortened_name = '_'.join(base_name.split()[:2])
    summarized_name = f"{shortened_name}_summarized.pdf"
    return summarized_name

# Function to extract relevant pages from a PDF
def extract_pages_from_pdf(uploaded_file, keywords):
    reader = PdfReader(uploaded_file)
    writer = PdfWriter()
    extracted_pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if any(keyword.lower() in text.lower() for keyword in keywords):
            extracted_pages.append(i)
            writer.add_page(page)

    if extracted_pages:
        output_buffer = BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)
        return output_buffer, len(extracted_pages)
    else:
        return None, 0

# Function to calculate total pages in a PDF
def count_pages(pdf_file):
    reader = PdfReader(pdf_file)
    return len(reader.pages)

# Title and Description
st.title("Sustainability Report Data Extraction Tool")

with st.expander("About the Tool"):
    st.write("""
    This utility extracts pages containing greenhouse gas (GHG) emissions data from PDFs. 
    This tool was developed to assist those researching corporate greenhouse gas emissions 
    to identify data-containing pages from these often lengthy documents (typically, only a 
    short page range contains the actual emissions data). The tool works by searching for 
    pages containing a dense array of numbers and then concatenates those into a single 
    summary PDF, which the tool presents for download.
    """)

with st.expander("Notes and Credits"):
    st.write("""
    As a program, its operation is imperfect. If you suspect that the results might not be 
    accurate or that some data was omitted from the summarized PDF, please check against 
    the source. The generated PDF is displayed on the screen and can then be downloaded by 
    using the button which populates after the extraction process.

    This tool was developed by Daniel Rosehill (danielrosehill.com) with the assistance of GPT 4o.
    """)

# Tab Navigation for Individual Mode and Batch Mode
mode = st.radio("Select Mode", ["Individual Mode", "Batch Mode"], horizontal=True)

keywords = ["GHG emissions", "Scope 1", "Scope 2", "Scope 3"]

if mode == "Individual Mode":
    uploaded_file = st.file_uploader("Upload a Sustainability Report (PDF)", type="pdf")

    if uploaded_file:
        output_buffer, _ = extract_pages_from_pdf(uploaded_file, keywords)

        if output_buffer:
            summarized_filename = generate_summarized_filename(uploaded_file.name)
            
            # Display Extracted PDF
            st.subheader("Extracted Pages")
            pdf_viewer(output_buffer.getvalue())
            
            # Download Button with dynamic file name
            st.download_button(
                label="Download Summarized Report",
                data=output_buffer,
                file_name=summarized_filename,
                mime="application/pdf"
            )
        else:
            st.warning("No relevant pages found with the specified keywords.")

elif mode == "Batch Mode":
    uploaded_files = st.file_uploader(
        "Upload up to 10 Sustainability Reports (PDFs)", type="pdf", accept_multiple_files=True
    )

    if uploaded_files:
        if len(uploaded_files) > 10:
            st.warning("You can upload a maximum of 10 files at a time.")
        else:
            total_pages_before = 0
            total_pages_after = 0

            zip_buffer = BytesIO()
            with ZipFile(zip_buffer, "w") as zip_file:
                for uploaded_file in uploaded_files:
                    # Count total pages before processing
                    pages_before = count_pages(uploaded_file)
                    total_pages_before += pages_before

                    # Extract relevant pages
                    output_buffer, pages_after = extract_pages_from_pdf(uploaded_file, keywords)
                    total_pages_after += pages_after

                    if output_buffer:
                        summarized_filename = generate_summarized_filename(uploaded_file.name)
                        zip_file.writestr(summarized_filename, output_buffer.getvalue())

            zip_buffer.seek(0)

            # Calculate metrics
            pages_reduced = total_pages_before - total_pages_after
            reduction_percentage = (pages_reduced / total_pages_before * 100) if total_pages_before > 0 else 0

            # Display metrics
            st.subheader("Batch Processing Summary")
            st.write(f"**Total Pages Before Processing:** {total_pages_before}")
            st.write(f"**Total Pages After Processing:** {total_pages_after}")
            st.write(f"**Pages Reduced:** {pages_reduced}")
            st.write(f"**Reduction Percentage:** {reduction_percentage:.2f}%")

            # Download ZIP file containing all summarized PDFs
            st.download_button(
                label="Download All Summarized Reports as ZIP",
                data=zip_buffer,
                file_name="summarized_reports.zip",
                mime="application/zip"
            )

st.markdown(footer, unsafe_allow_html=True)
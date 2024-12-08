import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
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
    # Extract the base name without extension
    base_name = original_filename.split('.')[0]
    # Take the first word or two from the base name
    shortened_name = '_'.join(base_name.split()[:2])
    # Append '_summarized' to the shortened name
    summarized_name = f"{shortened_name}_summarized.pdf"
    return summarized_name

# Title and Description
st.title("Sustainability Report Data Extraction Tool")
import streamlit as st

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

# File Uploader
uploaded_file = st.file_uploader("Upload a Sustainability Report (PDF)", type="pdf")

if uploaded_file:
    # Load PDF
    reader = PdfReader(uploaded_file)
    writer = PdfWriter()
    extracted_pages = []
    
    # Keywords for identification
    keywords = ["GHG emissions", "Scope 1", "Scope 2", "Scope 3"]
    
    # Process each page
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if any(keyword.lower() in text.lower() for keyword in keywords):
            extracted_pages.append(i)
            writer.add_page(page)
    
    # Save extracted pages to a new PDF
    if extracted_pages:
        output_buffer = BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)
        
        # Generate summarized file name
        original_filename = uploaded_file.name
        summarized_filename = generate_summarized_filename(original_filename)
        
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


st.markdown(footer, unsafe_allow_html=True)
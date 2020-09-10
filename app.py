import streamlit as st
import pandas as pd
import pdfplumber

st.title('DSQ to GesPhar')

st.set_option('deprecation.showfileUploaderEncoding', False)

def extract_tables(feed):
    data = []
    with pdfplumber.open(feed) as pdf:
        pages = pdf.pages
        for p in pages:
            data.append(p.extract_tables())
    return pages[0].extract_words(), pd.DataFrame(data[0][0][1:], columns=data[0][0][0])

# def extract_demographics(feed):
#     with pdfplumber.open(feed) as pdf:
#         first_page = pdf.pages[0]
#     return first_page.extract_text()

uploaded_file = st.sidebar.file_uploader('Choose your .pdf file', type="pdf")
if uploaded_file is not None:
    text, df = extract_tables(uploaded_file)
    dob = text[4]['text']
    lastname = text[5]['text']
    firstname = text[6]['text']
    gender = text[7]['text']

    # demographics = extract_demographics(uploaded_file)
    # st.write(demographics)

    st.header(lastname+' '+firstname)
    st.subheader(dob)

# st.table(df)

    for x in df.itertuples():
        st.checkbox(x[4]+'\n'+x[5], value=False, key='checkbox'+str(x.Index))
        # st.write(x)

else:
    st.subheader('Select a PDF from the left')

import streamlit.components.v1 as components

# embed streamlit docs in a streamlit app
components.iframe("https://docs.streamlit.io/en/latest", width=1400, height=1024, scrolling=True)
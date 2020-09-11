import streamlit as st
import pandas as pd
import pdfplumber
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.title('DSQ to GesPhar')

st.set_option('deprecation.showfileUploaderEncoding', False)

# verbose = st.sidebar.checkbox(label='Include explanations', value=True)
verbose = True

formulary = pd.read_csv('jgh-formulary-non-restricted.csv')
# st.write(formulary)
formulary_meds = [formulary.Medication.tolist()][0]

def extract_pdf_data(feed):
    data = []
    with pdfplumber.open(feed) as pdf:
        pages = pdf.pages
        headers = pages[0].extract_table()[0]
        for p in pages:
            for line in p.extract_table()[1:]:
              data.append(line)
        text = pages[0].extract_text()
        df = pd.DataFrame(data, columns=headers)
    return df, text

# def extract_demographics(feed):
#     with pdfplumber.open(feed) as pdf:
#         first_page = pdf.pages[0]
#     return first_page.extract_text()

if verbose:
    st.subheader('Introduction')
    st.markdown('''The DSQ seems to be an inpenetrable fortress - no easy way to access its data. 
    The only reasonable way to get the medication list out is actually the same way we always did, 
    via PDF from the 'Impression pour Établissement' button. We'll then use some basic programming 
    to read the medication list from the PDF, then match each one to available medications on our 
    formulary (when possible) - essentially the skeleton of a medication reconciliation. Since 
    GesPhaRxLite runs in Chrome, we can then program a Chrome Extension to input each medication 
    into the system. ''')
    st.markdown('''After poking around, I don't see any other way to input medications than via 
    'Add to list' - please let me know if there's some sort of import module.
    ''')
    st.markdown('''This web app was written in Python using the Streamlit package and hosted for 
    free on Heroku. It would be easy to run on the hospital's servers, accessible via Chrome just 
    like GespharxLite, that way no sensitive data would be transmitted over the internet.
    ''')

st.subheader("1. Save patient's medication list as PDF via 'Impression pour Établissement' button on DSQ")

st.subheader("2. Load the PDF")

uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")

st.markdown('You can use this anonymized sample: ')

if st.button('Load Sample PDF'):
    uploaded_file = 'john-doe.pdf'

sample_pdf = '[Link to Sample PDF](https://www.dropbox.com/s/syzc62irybqbhox/john-doe.pdf?dl=1)'
st.markdown(sample_pdf, unsafe_allow_html=True)

# iframe_url = st.sidebar.text_area('URL to display', "https://docs.streamlit.io/en/latest")

if uploaded_file is not None:
    df, text= extract_pdf_data(uploaded_file)
    # dob = text[4]['text']
    dob = '1950/01/01'
    # lastname = text[5]['text']
    lastname = 'DOE'
    # firstname = text[6]['text']
    firstname = 'John'
    # gender = text[7]['text']
    gender = 'M'

    # demographics = extract_demographics(uploaded_file)
    # st.write(demographics)

st.subheader("3. Confirm we have the correct patient")
if uploaded_file is not None:

    st.write('i.e. '+lastname + ', ' + firstname + ' - ' + dob)
    # st.subheader('')

    # st.write(text)

st.subheader("4. Extract the medication list from the PDF")

st.markdown('''Using a package called PDFPlumber, we extract the table of medications and save it 
as a Pandas dataframe (essentially a spreadsheet).
''')

if uploaded_file is not None:

    st.table(df)


st.subheader("5. Match each entry to a medication on our formulary")
st.markdown('''Here I'm using a spredsheet of the CIUSSS formulary that I found on the shared 
drive, but we should be using the list of medications in the 'Pharmacy drug list' that populates 
the 'Add to list' module within GespharxLite, as it seems to have many of the alternate names of 
medications (i.e. many forms of Aminosalicylic Acid on the formulary spreadsheet, but Aspirin
doesn't show up anywhere)
''')
st.markdown('''For now, I am using a basic 'Fuzzy Matching' algorithm to match the DSQ medication to a Formulary 
medication, but with a little work, this could be more sophisticated and much more reliable. Every time the 
algorithm doesn't find a match, or has to be corrected by the user, it will learn from that mistake and get
better over time. 
''')
st.markdown('''You'll see each medication in CAPS, followed by the JGH formulary medication
in green, accompanied by the matching algorithm score.
''')
if uploaded_file is not None:

    for x in df.itertuples():
        # st.checkbox(x[4] + '.....' + x[5], value=False, key='checkbox' + str(x.Index))
        medication = x[4]
        instructions = x[5]
        # st.write(medication.split('\n'))
        st.write(str(x.Index+1)+'. '+medication)
        # st.write(x[5])
        # remove_brand = re.sub(r'\([^)]*\)', '', x[4])
        # remove_comprime = remove_brand.replace('COMPRIME','').strip()
        # matches = process.extract(remove_comprime, formulary_meds, limit=5, scorer=fuzz.token_set_ratio)
        matches = process.extract(medication.split('\n')[0], formulary_meds, limit=5, scorer=fuzz.token_set_ratio)

        if matches[0][1] > 50:
            st.write(matches[0])
        else:
            brand = x[4][x[4].find("(") + 1:x[4].find(")")]
            matches2 = process.extract(brand, formulary_meds, limit=5, scorer=fuzz.token_set_ratio)
            if matches2[0][1] > 70:
                st.write(matches2[0])
            else:
                st.write('No matches')

st.subheader("6. Determine dose, route, frequency, etc. (In Progress)")
st.markdown('''Using similar algorithms and basic natural language processing (NLP) techniques, 
along with some AI/Machine Learning, to decipher dose, route, frequency, duration from the DSQ free text.
''')
st.markdown('''i.e. Take 1 tablet once daily before bedtime (cholesterol) = 1 tab po hs
''')
if uploaded_file is not None:
    st.table(df.Posologie)

st.subheader("7. Implement built-in logic to identify duplicates, expired medications, etc. (In Progress)")

st.subheader("8. Build a Chrome Extension that interfaces between our Web App and GespharxLite (In Progress)")
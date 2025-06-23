import streamlit as st
from autocorrect_logic import load_symspell, autocorrect_text  # Import your functions

# Initialize SymSpell (load the dictionary)
st.title("Interactive Autocorrect Tool")
@st.cache_resource
def get_symspell():
    return load_symspell()

sym_spell = get_symspell()

# Streamlit App


user_text = st.text_area("Enter your text here:", height=200)  # Text area for user input

if st.button("Autocorrect"):  # Button to trigger the autocorrection
    if user_text:
        corrected_text, corrections = autocorrect_text(user_text, sym_spell)
        st.subheader("Corrected Text:")
        st.write(corrected_text)

        if corrections:
            st.subheader("Corrections Made:")
            for original, corrected in corrections.items():
                st.write(f"'{original}' -> '{corrected}'")
        else:
            st.write("No corrections were needed.")
    else:
        st.warning("Please enter some text to autocorrect")
        
    
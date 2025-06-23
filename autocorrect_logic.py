import streamlit as st
import pkg_resources
import os
from symspellpy import Verbosity, SymSpell
import urllib.request
import io
import zipfile

def load_symspell(dictionary_path=None, bigram_path=None):
    """Loads the SymSpell spell checker with a dictionary."""
    try:
        sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    except ImportError:
        print("Error: SymSpell is not installed. Please install symspellpy.")
        return None

    if dictionary_path is None:
        print("Using default dictionary: frequency_dictionary_en_82_765.txt")
        dictionary_path = "frequency_dictionary_en_82_765.txt"

    # Construct the full path 
    try:
        dictionary_path = pkg_resources.resource_filename("symspellpy", dictionary_path)
    except FileNotFoundError:
        print(
            f"Error: Dictionary file '{dictionary_path}' not found within the symspellpy package. Attempting to download..."
        )
        # Download and extract
        try:
            url = "https://github.com/wolfgarbe/SymSpell/releases/download/v6.7.0/frequency_dictionary_en_82_765.txt.zip"
            with urllib.request.urlopen(url) as response:
                zip_data = response.read()
            with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
                zf.extract("frequency_dictionary_en_82_765.txt")  # Extract the dictionary
            print("Downloaded and extracted dictionary.")
            dictionary_path = "frequency_dictionary_en_82_765.txt" #set the path
        except Exception as e:
            print(f"Error downloading or extracting dictionary: {e}")
            print("Please download the dictionary manually and place it in the same directory as your script, or specify the path.")
            return None

    if not os.path.exists(dictionary_path):
        print(f"Error: Dictionary file not found at the specified path: {dictionary_path}")
        return None

    try:
        if not sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1):
            print(f"Error loading dictionary at: {dictionary_path}")
            return None

        if bigram_path:
            try:
                bigram_path = pkg_resources.resource_filename("symspellpy", bigram_path)
            except FileNotFoundError:
                print(
                    f"Error: Bigram dictionary file '{bigram_path}' not found within the symspellpy package."
                )
                bigram_path = None
            if bigram_path and os.path.exists(bigram_path):
                sym_spell.load_bigram_dictionary(
                    bigram_path, term_index=0, count_index=2
                )
            elif bigram_path:
                print(
                    f"Error: Bigram dictionary file not found at the specified path: {bigram_path}"
                )

        return sym_spell
    except Exception as e:
        print(f"An error occurred while loading the dictionary: {e}")
        return None


def autocorrect_text(text, sym_spell):
    """Autocorrects the given text using SymSpell."""
    if not sym_spell:
        return text, {}

    words = text.split()
    corrected_words = []
    corrections_made = {}

    for word in words:
        cleaned_word = "".join(char for char in word if char.isalnum()).lower()
        if cleaned_word:
            suggestions = sym_spell.lookup(
                cleaned_word, Verbosity.CLOSEST, max_edit_distance=2
            )
            if suggestions and suggestions[0].term != cleaned_word:
                corrected_word = suggestions[0].term
                corrected_words.append(corrected_word)
                corrections_made[word] = corrected_word
            else:
                corrected_words.append(word)
        else:
            corrected_words.append(word)

    return " ".join(corrected_words), corrections_made
# Initialize SymSpell (load the dictionary)
@st.cache_resource
def get_symspell():
    return load_symspell()

sym_spell = get_symspell()

# Streamlit App
st.title("Interactive Autocorrect Tool")  # Set the title of the app

user_text = st.text_area("Enter the text you want to autocorrect:", height=200)  # Text area for user input

if st.button("Autocorrect", key="autocorrect_button"):  # Add a unique key here
    if sym_spell:
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
        st.error("Failed to load the SymSpell dictionary. Please check the dictionary file path.")


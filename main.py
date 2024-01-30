import streamlit as st
from wordcloud import WordCloud
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
import re
import matplotlib.pyplot as plt
from collections import Counter

# Download NLTK resources
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

# Function to generate word cloud from adjectives
def generate_adjective_wordcloud(text):
    blob = TextBlob(text)
    adjectives = [word.lower() for (word, pos) in blob.tags if pos.startswith('JJ')]
    
    if adjectives:
        adjective_text = ' '.join(adjectives)
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(adjective_text)
        fig, ax = plt.subplots(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.warning("No adjectives found.")

# Function to remove custom words from text
def remove_custom_words(text, custom_words):
    for word in custom_words:
        text = text.replace(word, '')
    return text

# Function to remove numbers and symbols from text
def remove_numbers_and_symbols(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

# Function to analyze word frequency
def analyze_word_frequency(text, top_n=10):
    adjectives = [word.lower() for (word, pos) in TextBlob(text).tags if pos.startswith('JJ')]
    word_freq = Counter(adjectives)
    return dict(word_freq.most_common(top_n))

# Function to perform sentiment analysis
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    return sentiment_score

# Streamlit app
st.title("Adjective Analytics from Product and Service Reviews")

# Text input area or file upload
text_input_method = st.radio("Choose input method:", ("Direct Text Input", "Upload Text File"))

if text_input_method == "Direct Text Input":
    user_input = st.text_area("Paste Text", value="", height=200, help="Enter your product or service reviews here.")
else:
    uploaded_file = st.file_uploader("Upload a Text File (.txt)", type=["txt"])
    if uploaded_file is not None:
        user_input = uploaded_file.read().decode("utf-8")
    else:
        user_input = ""

# Checkbox to remove stopwords
remove_stopwords = st.checkbox("Remove Common English Stopwords")

# Custom words to remove
custom_words_to_remove = st.text_area(
    "Enter words to remove (comma-separated)",
    help="Provide a list of custom words to be removed, separated by commas.",
)

# Convert custom words to a list
custom_words = [word.strip() for word in custom_words_to_remove.split(',')]

# Extract adjectives and generate analytics when the user clicks the button
if st.button("Generate Adjective Analytics", help="Click to extract adjectives and generate analytics."):
    with st.spinner("Generating..."):
        if user_input:
            if remove_stopwords:
                stop_words = set(stopwords.words("english"))
                user_input = ' '.join([word for word in user_input.split() if word.lower() not in stop_words])

            if custom_words:
                user_input = remove_custom_words(user_input, custom_words)

            user_input = remove_numbers_and_symbols(user_input)

            generate_adjective_wordcloud(user_input)

            # Analyze and display word frequency
            st.subheader("Adjective Frequency Analysis")
            adjective_freq = analyze_word_frequency(user_input, top_n=10)
            st.table(adjective_freq)

            # Perform sentiment analysis and display the result
            st.subheader("Sentiment Analysis")
            sentiment_score = analyze_sentiment(user_input)
            if sentiment_score > 0:
                sentiment_label = "Positive"
            elif sentiment_score < 0:
                sentiment_label = "Negative"
            else:
                sentiment_label = "Neutral"
            st.write(f"Overall Sentiment: {sentiment_label} (Score: {sentiment_score:.2f})")

            # Additional Analytics and Storytelling

            # Example Story: Positive Sentiment
            if sentiment_score > 0:
                st.write("The sentiment analysis indicates a positive tone in the text. This positivity can be leveraged "
                         "for branding and marketing strategies. Consider emphasizing these positive aspects in your "
                         "communication to enhance customer engagement.")

            # Example Story: Negative Sentiment
            elif sentiment_score < 0:
                st.write("The sentiment analysis suggests a negative tone in the text. It's crucial to identify and address "
                         "the sources of negativity. Engaging with customers to understand their concerns can be valuable in "
                         "improving overall satisfaction.")

            # Example Story: Neutral Sentiment
            else:
                st.write("The overall sentiment is neutral. While neutrality is balanced, it's essential to explore specific "
                         "topics or keywords that might require attention or further analysis. Consider focusing on areas "
                         "that can be improved or enhanced.")

        else:
            st.warning("Please enter some text or upload a text file.")

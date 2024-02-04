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

# Function to analyze named entity frequency
def analyze_named_entity_frequency(text, top_n=10):
    entities = [ent for ent in TextBlob(text).noun_phrases]
    entity_freq = Counter(entities)
    return dict(entity_freq.most_common(top_n))

# Streamlit app
st.title("Airline Review Analytics")

# Text input area or file upload
text_input_method = st.radio("Choose input method:", ("Direct Text Input", "Upload Text File"))

if text_input_method == "Direct Text Input":
    user_input = st.text_area("Paste Text", value="", height=200, help="Enter your airline reviews here.")
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

# Initialize sentiment_score outside the button click block
sentiment_score = 0.0

# Extract adjectives and generate analytics when the user clicks the button
if st.button("Generate Airline Review Analytics", help="Click to extract adjectives and generate analytics."):
    with st.spinner("Generating..."):
        if user_input:
            # Remove stopwords and custom words
            if remove_stopwords:
                stop_words = set(stopwords.words("english"))
                user_input = ' '.join([word for word in user_input.split() if word.lower() not in stop_words])

            if custom_words:
                user_input = remove_custom_words(user_input, custom_words)

            # Remove numbers and symbols
            user_input = remove_numbers_and_symbols(user_input)

            # Generate word cloud
            generate_adjective_wordcloud(user_input)

            # Display bar chart for word frequency
            st.subheader("Adjective Frequency Analysis")
            adjective_freq = analyze_word_frequency(user_input, top_n=10)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(adjective_freq.keys(), adjective_freq.values())
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)

            # Visualize sentiment scores
            st.subheader("Sentiment Analysis Visualization")
            sentiment_scores = [analyze_sentiment(review) for review in user_input.split('\n')]
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(sentiment_scores)
            ax.set_xlabel('Review Number')
            ax.set_ylabel('Sentiment Score')
            st.pyplot(fig)

            # Named Entity Recognition (NER) and display the entities
            st.subheader("Named Entities Analysis")
            entity_freq = analyze_named_entity_frequency(user_input)
            if entity_freq:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.barh(list(entity_freq.keys()), list(entity_freq.values()))
                ax.set_xlabel('Frequency')
                ax.set_ylabel('Named Entities')
                st.pyplot(fig)
            else:
                st.warning("No named entities found.")

            # Analysis and Suggestions based on Named Entities
            if any("airline" in entity.lower() for entity in entity_freq.keys()):
                st.write("Customers frequently mention the airline, indicating a strong brand presence.")
            else:
                st.write("Consider promoting the airline brand more prominently in marketing materials.")

            if any(location in entity_freq.keys() for location in ["airport", "city", "destination"]):
                st.write("Locations are frequently mentioned. Explore marketing opportunities related to popular destinations.")
            
            # Additional Analytics and Storytelling

            # Example Story: Positive Sentiment
            if sentiment_score > 0:
                st.write("The sentiment analysis indicates a positive tone in the reviews. This positivity can be leveraged "
                         "for marketing strategies. Consider highlighting these positive aspects in your promotions and advertisements.")

            # Example Story: Negative Sentiment
            elif sentiment_score < 0:
                st.write("The sentiment analysis suggests a negative tone in the reviews. Addressing the sources of negativity "
                         "is crucial. Engaging with customers to understand their concerns can help improve overall satisfaction.")

            # Example Story: Neutral Sentiment
            else:
                st.write("The overall sentiment is neutral. While neutrality is balanced, it's essential to explore specific "
                         "topics or keywords that might require attention or further analysis. Consider focusing on areas "
                         "that can be improved or enhanced.")

        else:
            st.warning("Please enter some text or upload a text file.")

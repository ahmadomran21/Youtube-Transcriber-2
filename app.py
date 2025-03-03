import streamlit as st
import re
from collections import Counter
import pandas as pd

def analyze_keywords(text, min_occurrences=3):
    """Analyze keywords that appear more than a specified number of times."""
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and special characters
    text = re.sub(r'[^\w\s]', '', text)
    
    # Split into words
    words = text.split()
    
    # Filter out common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
        'has', 'have', 'had', 'be', 'been', 'being', 'in', 'on', 'at', 'to',
        'for', 'with', 'by', 'about', 'like', 'from', 'of', 'that', 'this',
        'these', 'those', 'it', 'its', 'it\'s', 'they', 'them', 'their',
        'we', 'us', 'our', 'i', 'my', 'me', 'mine', 'you', 'your', 'yours'
    }
    
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count occurrences
    word_counts = Counter(filtered_words)
    
    # Filter to words that appear more than min_occurrences times
    frequent_words = {word: count for word, count in word_counts.items() if count >= min_occurrences}
    
    # Sort by frequency (descending)
    sorted_words = dict(sorted(frequent_words.items(), key=lambda item: item[1], reverse=True))
    
    return sorted_words

# Set page configuration
st.set_page_config(
    page_title="Text & Keyword Analyzer",
    page_icon="📝",
    layout="wide"
)

# Page header
st.title("Text & Keyword Analyzer")

# Instructions for YouTube transcript
st.markdown("""
## How to use this tool with YouTube videos:

1. Go to the YouTube video you want to analyze
2. Under the video, click the "..." button
3. Select "Show transcript"
4. Copy the entire transcript
5. Paste it in the text area below
6. Adjust the minimum keyword occurrences if needed
7. Click "Analyze Text"
""")

# Input form
with st.form("text_form"):
    col1, col2 = st.columns([4, 1])
    
    with col1:
        text_input = st.text_area("Paste your text or YouTube transcript here:", height=200)
    
    with col2:
        min_occurrences = st.slider("Minimum occurrences", min_value=2, max_value=10, value=3)
        st.write("Adjust this slider to set how many times a word must appear to be included in the analysis.")
    
    submitted = st.form_submit_button("Analyze Text")

# Process the text when form is submitted
if submitted and text_input:
    # Analyze keywords
    keywords = analyze_keywords(text_input, min_occurrences)
    
    # Display some text stats
    word_count = len(text_input.split())
    st.info(f"Text contains {word_count} words and {len(keywords)} keywords that appear at least {min_occurrences} times.")
    
    # Display results in tabs
    tab1, tab2 = st.tabs(["Keyword Analysis", "Text Statistics"])
    
    with tab1:
        st.header("Keyword Analysis")
        
        if keywords:
            # Create columns for better visualization
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Create a table with keywords and counts
                st.subheader("Keyword Frequencies")
                
                # Convert to a dataframe for display
                keywords_data = {"Keyword": [], "Count": []}
                for word, count in keywords.items():
                    keywords_data["Keyword"].append(word)
                    keywords_data["Count"].append(count)
                
                df = pd.DataFrame(keywords_data)
                st.dataframe(df, use_container_width=True)
            
            with col2:
                # Display total unique keywords found
                st.metric("Total Keywords Found", len(keywords))
                
                if len(keywords) > 0:
                    top_keyword, top_count = list(keywords.items())[0]
                    st.metric("Most Frequent Keyword", f"{top_keyword} ({top_count} times)")
                
                # Create a bar chart for top keywords
                if len(keywords) > 0:
                    st.subheader("Top Keywords")
                    # Take top 10 or fewer
                    top_n = min(10, len(keywords))
                    top_keywords = dict(list(keywords.items())[:top_n])
                    
                    chart_data = pd.DataFrame({
                        "Keyword": list(top_keywords.keys()),
                        "Count": list(top_keywords.values())
                    })
                    
                    st.bar_chart(data=chart_data, x="Keyword", y="Count")
        else:
            st.info("No keywords found with the specified minimum occurrences.")
    
    with tab2:
        st.header("Text Statistics")
        
        # Count characters
        char_count = len(text_input)
        
        # Count sentences (roughly)
        sentence_count = len(re.split(r'[.!?]+', text_input)) - 1
        
        # Calculate metrics
        metrics = {
            "Total Characters": char_count,
            "Total Words": word_count,
            "Approximate Sentences": max(1, sentence_count),
            "Average Word Length": round(sum(len(word) for word in text_input.split()) / max(1, word_count), 1),
            "Words Per Sentence": round(word_count / max(1, sentence_count), 1)
        }
        
        # Display metrics
        col1, col2 = st.columns(2)
        
        for i, (metric, value) in enumerate(metrics.items()):
            if i % 2 == 0:
                col1.metric(metric, value)
            else:
                col2.metric(metric, value)

# Add footer
st.markdown("---")
st.markdown("Created with ❤️ using Streamlit")

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
    
    # Comprehensive list of stop words to filter out
    stop_words = {
        # Articles
        'a', 'an', 'the',
        
        # Pronouns
        'i', 'me', 'my', 'mine', 'myself',
        'you', 'your', 'yours', 'yourself', 'yourselves',
        'he', 'him', 'his', 'himself',
        'she', 'her', 'hers', 'herself',
        'it', 'its', 'itself',
        'we', 'us', 'our', 'ours', 'ourselves',
        'they', 'them', 'their', 'theirs', 'themselves',
        'this', 'that', 'these', 'those', 'which', 'who', 'whom',
        
        # Prepositions
        'in', 'on', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 
        'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 
        'from', 'up', 'down', 'of', 'off', 'over', 'under',
        
        # Conjunctions
        'and', 'but', 'or', 'nor', 'so', 'yet', 'as', 'than',
        
        # Common verbs
        'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall', 'should',
        'can', 'could', 'may', 'might', 'must', 'ought',
        'go', 'goes', 'going', 'gone', 'went',
        'come', 'comes', 'coming', 'came',
        'get', 'gets', 'getting', 'got', 'gotten',
        'make', 'makes', 'making', 'made',
        'say', 'says', 'saying', 'said',
        'know', 'knows', 'knowing', 'knew', 'known',
        'think', 'thinks', 'thinking', 'thought',
        'take', 'takes', 'taking', 'took', 'taken',
        'see', 'sees', 'seeing', 'saw', 'seen',
        'want', 'wants', 'wanting', 'wanted',
        'look', 'looks', 'looking', 'looked',
        'use', 'uses', 'using', 'used',
        
        # Adverbs
        'very', 'really', 'just', 'now', 'then', 'here', 'there', 'when', 'where', 'why',
        'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'some', 'such', 'no',
        'not', 'only', 'same', 'so', 'than', 'too', 'well',
        
        # Numbers as words
        'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
        'first', 'second', 'third', 'fourth', 'fifth',
        
        # YouTube-specific common words
        'like', 'subscribe', 'channel', 'video', 'comment', 'youtube', 'watch', 'click',
        'today', 'gonna', 'let', 'tell', 'talk', 'show', 'thanks', 'thank'
    }
    
    # Filter out stop words and short words (less than 3 chars)
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
    page_title="YouTube Keyword Analyzer",
    page_icon="📊",
    layout="wide"
)

# Page header
st.title("YouTube Content Keyword Analyzer")
st.markdown("""
This tool analyzes text to find distinctive keywords that might trigger YouTube's algorithm.
It filters out common words, pronouns, and general verbs to focus on the meaningful content.
""")

# Instructions for YouTube transcript
with st.expander("How to get a YouTube transcript"):
    st.markdown("""
    ## How to get a transcript from YouTube:

    1. Go to the YouTube video you want to analyze
    2. Under the video, click the "..." button (or "More actions")
    3. Select "Show transcript"
    4. The transcript panel will open to the right of the video
    5. Click the three dots (⋮) in the transcript panel
    6. Select "Toggle timestamps" to hide timestamps if you want cleaner text
    7. Select all text in the transcript panel (Ctrl+A or Cmd+A)
    8. Copy the selected text (Ctrl+C or Cmd+C)
    9. Paste it in the text area below
    """)

# Input form
with st.form("text_form"):
    col1, col2 = st.columns([4, 1])
    
    with col1:
        text_input = st.text_area("Paste your YouTube transcript here:", height=200)
    
    with col2:
        min_occurrences = st.slider("Minimum occurrences", min_value=2, max_value=15, value=3)
        st.write("Adjust this slider to set how many times a keyword must appear to be included in the analysis.")
    
    submitted = st.form_submit_button("Analyze Keywords")

# Process the text when form is submitted
if submitted and text_input:
    # Analyze keywords
    keywords = analyze_keywords(text_input, min_occurrences)
    
    # Display some text stats
    word_count = len(text_input.split())
    st.info(f"Text contains {word_count} total words. Found {len(keywords)} distinctive keywords that appear at least {min_occurrences} times.")
    
    if keywords:
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Visualization", "Detailed Results"])
        
        with tab1:
            st.header("Keyword Visualization")
            
            # Take top 15 or fewer keywords for chart
            top_n = min(15, len(keywords))
            top_keywords = dict(list(keywords.items())[:top_n])
            
            chart_data = pd.DataFrame({
                "Keyword": list(top_keywords.keys()),
                "Frequency": list(top_keywords.values())
            })
            
            # Create bar chart
            st.bar_chart(data=chart_data, x="Keyword", y="Frequency", use_container_width=True)
            
            # Create metrics for key insights
            if len(keywords) > 0:
                st.subheader("Key Insights")
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                
                # Top keyword
                top_keyword, top_count = list(keywords.items())[0]
                metrics_col1.metric("Most Frequent Keyword", f"{top_keyword}", f"{top_count} times")
                
                # Second keyword if available
                if len(keywords) > 1:
                    second_keyword, second_count = list(keywords.items())[1]
                    metrics_col2.metric("Second Most Frequent", f"{second_keyword}", f"{second_count} times")
                
                # Third keyword if available
                if len(keywords) > 2:
                    third_keyword, third_count = list(keywords.items())[2]
                    metrics_col3.metric("Third Most Frequent", f"{third_keyword}", f"{third_count} times")
        
        with tab2:
            st.header("Detailed Keyword Results")
            
            # Convert to a dataframe for display
            keywords_data = {"Keyword": [], "Frequency": [], "Percentage of Content": []}
            
            for word, count in keywords.items():
                keywords_data["Keyword"].append(word)
                keywords_data["Frequency"].append(count)
                # Calculate percentage of content (based on total words)
                percentage = (count / word_count) * 100
                keywords_data["Percentage of Content"].append(f"{percentage:.2f}%")
            
            df = pd.DataFrame(keywords_data)
            st.dataframe(df, use_container_width=True)
            
            # Export options
            st.download_button(
                label="Download as CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='youtube_keywords.csv',
                mime='text/csv',
            )
    else:
        st.warning("No distinctive keywords found with the specified minimum occurrences. Try lowering the minimum occurrences threshold.")

# Add tips for YouTube optimization
with st.expander("Tips for YouTube SEO"):
    st.markdown("""
    ## How to use these keywords for YouTube optimization:
    
    1. **Video Title**: Include your top 1-2 keywords in your title
    2. **Description**: Include your top 5-7 keywords naturally in your description
    3. **Tags**: Add all relevant keywords from the analysis as tags
    4. **Transcript/Captions**: Make sure your video has accurate captions containing these keywords
    5. **Thumbnail**: Consider including your top keyword in your thumbnail if appropriate
    6. **Hashtags**: Use your top 3 keywords as hashtags in your description
    
    Remember that YouTube's algorithm looks for **relevance**, **consistency**, and **viewer engagement**. Keywords are just one part of the equation!
    """)

# Add footer
st.markdown("---")
st.markdown("Created with ❤️ using Streamlit")

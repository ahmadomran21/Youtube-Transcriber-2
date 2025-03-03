import streamlit as st
import re
from collections import Counter
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(youtube_url):
    """Extract the video ID from a YouTube URL."""
    parsed_url = urlparse(youtube_url)
    
    if parsed_url.netloc == 'youtu.be':
        return parsed_url.path[1:]
    
    if parsed_url.netloc in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    
    # If we get here, we didn't find a valid video ID
    raise ValueError(f"Could not extract video ID from URL: {youtube_url}")

def get_transcript(youtube_url):
    """Get the transcript of a YouTube video."""
    try:
        video_id = extract_video_id(youtube_url)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine all transcript pieces into a single text
        transcript_text = ' '.join([item['text'] for item in transcript_list])
        
        return transcript_text
    except Exception as e:
        st.error(f"Error getting transcript: {str(e)}")
        return None

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
    page_title="YouTube Transcript Analyzer",
    page_icon="🎥",
    layout="wide"
)

# Page header
st.title("YouTube Transcript & Keyword Analyzer")
st.markdown("Enter a YouTube URL to transcribe the video and analyze keyword frequency.")

# Input form
with st.form("youtube_form"):
    youtube_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    min_occurrences = st.slider("Minimum keyword occurrences", min_value=2, max_value=10, value=3)
    submitted = st.form_submit_button("Analyze Video")

# Process the video when form is submitted
if submitted and youtube_url:
    try:
        # Show spinner while processing
        with st.spinner("Processing video... This may take a minute."):
            # Get transcript
            transcript = get_transcript(youtube_url)
            
            if not transcript:
                st.error("Failed to retrieve transcript. Make sure the video has captions available.")
            else:
                # Analyze keywords
                keywords = analyze_keywords(transcript, min_occurrences)
                
                # Display results in tabs
                tab1, tab2 = st.tabs(["Transcript", "Keywords"])
                
                with tab1:
                    st.header("Video Transcript")
                    st.text_area("", transcript, height=400)
                    
                with tab2:
                    st.header("Keyword Analysis")
                    
                    if keywords:
                        # Create columns for better visualization
                        col1, col2 = st.columns([3, 2])
                        
                        with col1:
                            # Create a table with keywords and counts
                            st.subheader("Keyword Frequencies")
                            
                            # Convert to a format that's good for display
                            keywords_data = {"Keyword": [], "Count": []}
                            for word, count in keywords.items():
                                keywords_data["Keyword"].append(word)
                                keywords_data["Count"].append(count)
                            
                            # Display as a dataframe
                            import pandas as pd
                            df = pd.DataFrame(keywords_data)
                            st.dataframe(df, use_container_width=True)
                        
                        with col2:
                            # Display total unique keywords found
                            st.metric("Total Keywords Found", len(keywords))
                            
                            if len(keywords) > 0:
                                top_keyword, top_count = list(keywords.items())[0]
                                st.metric("Most Frequent Keyword", f"{top_keyword} ({top_count} times)")
                    else:
                        st.info("No keywords found with the specified minimum occurrences.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Add footer
st.markdown("---")
st.markdown("Created with ❤️ using Streamlit")

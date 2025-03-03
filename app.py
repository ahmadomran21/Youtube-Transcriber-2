import streamlit as st
import json
from youtube_transcriber import YouTubeTranscriber

# Set page configuration
st.set_page_config(
    page_title="YouTube Transcriber & Keyword Analyzer",
    page_icon="🎥",
    layout="wide"
)

# Page header
st.title("YouTube Transcriber & Keyword Analyzer")
st.markdown("Enter a YouTube URL to transcribe the video, proofread the transcript, and analyze keyword frequency.")

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
            transcriber = YouTubeTranscriber()
            result = transcriber.process_video(youtube_url, min_occurrences, 'json')
            
        if not result.get('success', False):
            st.error(f"Error: {result.get('message', 'Failed to process video')}")
        else:
            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["Video Info", "Transcript", "Keywords"])
            
            with tab1:
                st.header("Video Information")
                st.subheader(result['video_title'])
                st.markdown(f"[Open on YouTube]({result['video_url']})")
                
            with tab2:
                st.header("Transcript")
                original_col, corrected_col = st.columns(2)
                
                with original_col:
                    st.subheader("Original Transcript")
                    st.text_area("", result['transcript']['original'], height=400)
                
                with corrected_col:
                    st.subheader("Corrected Transcript")
                    st.text_area("", result['transcript']['corrected'], height=400)
                
                st.info(f"Corrections made: {result['transcript']['correction_count']}")
                
            with tab3:
                st.header("Keyword Analysis")
                
                if result['keywords']:
                    # Prepare data for chart
                    keywords = list(result['keywords'].keys())
                    counts = list(result['keywords'].values())
                    
                    # Create a dataframe for the chart
                    keyword_data = {"Keyword": keywords, "Count": counts}
                    
                    # Create bar chart
                    st.bar_chart(keyword_data, x="Keyword", y="Count", use_container_width=True)
                    
                    # Create a table with keywords and counts
                    st.subheader("Keyword Frequencies")
                    for word, count in result['keywords'].items():
                        st.markdown(f"**{word}**: {count} occurrences")
                else:
                    st.info("No keywords found with the specified minimum occurrences.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Add footer
st.markdown("---")
st.markdown("Created with ❤️ using Streamlit")

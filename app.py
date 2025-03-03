import streamlit as st
import json
import os
import re
from collections import Counter
from urllib.parse import urlparse, parse_qs
import language_tool_python
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi

# Define the YouTubeTranscriber class directly in app.py
class YouTubeTranscriber:
    def __init__(self):
        self.language_tool = language_tool_python.LanguageTool('en-US')
    
    def extract_video_id(self, youtube_url):
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

    def get_transcript(self, youtube_url):
        """Get the transcript of a YouTube video."""
        try:
            video_id = self.extract_video_id(youtube_url)
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Combine all transcript pieces into a single text
            transcript_text = ' '.join([item['text'] for item in transcript_list])
            
            return transcript_text
        except Exception as e:
            print(f"Error getting transcript: {e}")
            return None

    def get_video_title(self, youtube_url):
        """Get the title of a YouTube video."""
        try:
            video_id = self.extract_video_id(youtube_url)
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            return yt.title
        except Exception as e:
            print(f"Error getting video title: {e}")
            return "Unknown Video"

    def proofread_text(self, text):
        """Proofread the text using LanguageTool."""
        try:
            matches = self.language_tool.check(text)
            
            # Create a corrected version of the text
            corrected_text = text
            offset = 0
            
            # Sort matches by their position in the text to avoid offsetting issues
            for match in sorted(matches, key=lambda m: m.offset):
                # Get the suggested replacement (if any)
                if match.replacements:
                    replacement = match.replacements[0]
                    
                    # Calculate the position considering previous corrections
                    start = match.offset + offset
                    end = match.offset + match.errorLength + offset
                    
                    # Replace the error with the correction
                    corrected_text = corrected_text[:start] + replacement + corrected_text[end:]
                    
                    # Update the offset for future corrections
                    offset += len(replacement) - match.errorLength
            
            # Return both the original and corrected texts
            return {
                'original': text,
                'corrected': corrected_text,
                'correction_count': len(matches)
            }
        except Exception as e:
            print(f"Error proofreading text: {e}")
            return {
                'original': text,
                'corrected': text,
                'correction_count': 0
            }

    def analyze_keywords(self, text, min_occurrences=3):
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

    def process_video(self, youtube_url, min_occurrences=3, output_format='text'):
        """Process a YouTube video: get transcript, proofread, and analyze keywords."""
        # Get video title
        video_title = self.get_video_title(youtube_url)
        
        # Get transcript
        transcript = self.get_transcript(youtube_url)
        
        if not transcript:
            return {
                'success': False,
                'message': 'Failed to retrieve transcript'
            }
        
        # Proofread transcript
        proofread_result = self.proofread_text(transcript)
        
        # Analyze keywords
        keywords = self.analyze_keywords(transcript, min_occurrences)
        
        # Create result object
        result = {
            'success': True,
            'video_title': video_title,
            'video_url': youtube_url,
            'transcript': {
                'original': proofread_result['original'],
                'corrected': proofread_result['corrected'],
                'correction_count': proofread_result['correction_count']
            },
            'keywords': keywords
        }
        
        # Format output based on preference
        if output_format == 'json':
            return result
        else:  # text format
            output = []
            output.append(f"Title: {video_title}")
            output.append(f"URL: {youtube_url}")
            output.append("\n--- ORIGINAL TRANSCRIPT ---")
            output.append(proofread_result['original'])
            output.append("\n--- CORRECTED TRANSCRIPT ---")
            output.append(proofread_result['corrected'])
            output.append(f"\nCorrections made: {proofread_result['correction_count']}")
            output.append("\n--- KEYWORD ANALYSIS ---")
            
            if keywords:
                for word, count in keywords.items():
                    output.append(f"'{word}': {count} occurrences")
            else:
                output.append("No keywords found with the specified minimum occurrences.")
            
            return '\n'.join(output)

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
                    chart_data = {"Keyword": keywords, "Count": counts}
                    
                    # Display the data
                    st.bar_chart(data=chart_data, x="Keyword", y="Count")
                    
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

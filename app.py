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
        'this', 'that', 'these', 'those', 'which', 'who', 'whom', 'what', 'whose',
        'who\'s', 'what\'s', 'that\'s', 'there\'s', 'here\'s',
        
        # Prepositions
        'in', 'on', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 
        'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 
        'from', 'up', 'down', 'of', 'off', 'over', 'under', 'out',
        
        # Conjunctions
        'and', 'but', 'or', 'nor', 'so', 'yet', 'as', 'than', 'because', 'while',
        
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
        'tell', 'tells', 'telling', 'told',
        'try', 'tries', 'trying', 'tried',
        'ask', 'asks', 'asking', 'asked',
        'need', 'needs', 'needing', 'needed',
        'feel', 'feels', 'feeling', 'felt',
        'become', 'becomes', 'becoming', 'became',
        'leave', 'leaves', 'leaving', 'left',
        'put', 'puts', 'putting',
        'mean', 'means', 'meaning', 'meant',
        'keep', 'keeps', 'keeping', 'kept',
        'let', 'lets', 'letting',
        'begin', 'begins', 'beginning', 'began', 'begun',
        'seem', 'seems', 'seeming', 'seemed',
        'help', 'helps', 'helping', 'helped',
        'talk', 'talks', 'talking', 'talked',
        'turn', 'turns', 'turning', 'turned',
        'start', 'starts', 'starting', 'started',
        'show', 'shows', 'showing', 'showed', 'shown',
        'hear', 'hears', 'hearing', 'heard',
        'play', 'plays', 'playing', 'played',
        'run', 'runs', 'running', 'ran',
        'move', 'moves', 'moving', 'moved',
        'live', 'lives', 'living', 'lived',
        'believe', 'believes', 'believing', 'believed',
        'work', 'works', 'working', 'worked',
        'happen', 'happens', 'happening', 'happened',
        'done', 'doing', 'does', 
        
        # Contractions
        'isn\'t', 'aren\'t', 'wasn\'t', 'weren\'t', 'haven\'t', 'hasn\'t', 'hadn\'t',
        'don\'t', 'doesn\'t', 'didn\'t', 'won\'t', 'wouldn\'t', 'can\'t', 'couldn\'t',
        'shouldn\'t', 'mightn\'t', 'mustn\'t', 'they\'d', 'i\'d', 'we\'d', 'he\'d', 'she\'d',
        'you\'d', 'i\'ll', 'you\'ll', 'he\'ll', 'she\'ll', 'we\'ll', 'they\'ll',
        'i\'m', 'you\'re', 'he\'s', 'she\'s', 'it\'s', 'we\'re', 'they\'re',
        'i\'ve', 'you\'ve', 'we\'ve', 'they\'ve',
        
        # Adverbs
        'very', 'really', 'just', 'now', 'then', 'here', 'there', 'when', 'where', 'why',
        'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'some', 'such', 'no',
        'not', 'only', 'same', 'so', 'than', 'too', 'well', 'again', 'ever', 'far',
        'forward', 'fast', 'high', 'low', 'near', 'never', 'still', 'today',
        'tomorrow', 'yesterday', 'almost', 'always', 'quickly', 'finally',
        
        # Numbers as words
        'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
        'first', 'second', 'third', 'fourth', 'fifth', 'hundred', 'thousand', 'million',
        
        # YouTube-specific common words
        'like', 'subscribe', 'channel', 'video', 'comment', 'youtube', 'watch', 'click',
        'today', 'gonna', 'let', 'tell', 'talk', 'show', 'thanks', 'thank',
        
        # Additional words to filter based on user feedback
        'out', 'told', 'while', 'wasn\'t', 'asked', 'they\'d', 'done', 'tried', 'back', 'even', 'other', 'wasnt', 'since', 'didnt', 'away', 'also', 'once', 'enough', 'much', 'dont', 'around', 'mrs', 'until'
    }
    
    # Filter out stop words and short words (less than 3 chars)
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count occurrences
    word_counts = Counter(filtered_words)
    
    # Filter to words that appear more than min_occurrences times
    frequent_words = {word: count for word, count in word_counts.items() if count >= min_occurrences}
    
    # Sort by frequency (descending)
    sorted_words = dict(sorted(frequent_words.items(), key=lambda item: item[1], reverse=True))
    
    return sorted_words, word_counts

def find_common_keywords(all_keyword_counts, min_scripts, min_occurrences):
    """Find keywords that appear in multiple scripts with minimum occurrences."""
    if not all_keyword_counts:
        return {}
    
    # Get unique words across all scripts
    all_words = set()
    for counts in all_keyword_counts:
        all_words.update(counts.keys())
    
    # Find words that appear in at least min_scripts scripts with min_occurrences
    common_keywords = {}
    for word in all_words:
        # Count in how many scripts this word appears with min_occurrences
        script_count = sum(1 for counts in all_keyword_counts if counts.get(word, 0) >= min_occurrences)
        
        # If it appears in at least min_scripts scripts, add it to common_keywords
        if script_count >= min_scripts:
            # Calculate total occurrences across all scripts
            total_count = sum(counts.get(word, 0) for counts in all_keyword_counts)
            common_keywords[word] = total_count
    
    # Sort by total frequency
    sorted_common = dict(sorted(common_keywords.items(), key=lambda item: item[1], reverse=True))
    return sorted_common

# Set page configuration
st.set_page_config(
    page_title="Multi-Script YouTube Keyword Analyzer",
    page_icon="📊",
    layout="wide"
)

# Page header
st.title("Multi-Script YouTube Keyword Analyzer")
st.markdown("""
This tool analyzes multiple YouTube transcripts to find distinctive keywords and identify common patterns across videos.
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
    9. Paste it in one of the text areas below
    """)

# Main area for script input
st.header("Enter Your YouTube Transcripts")

# Create text areas for multiple scripts
tab_titles = ["Script 1", "Script 2", "Script 3", "Script 4", "Script 5", 
             "Script 6", "Script 7", "Script 8", "Script 9", "Script 10"]

script_tabs = st.tabs(tab_titles)
script_texts = []

for i, tab in enumerate(script_tabs):
    with tab:
        script_label = f"Enter Script {i+1}"
        if i == 0:
            script_label += " (Required)"
        
        script_text = st.text_area(script_label, height=150, key=f"script_{i}")
        script_texts.append(script_text)

# Analysis settings
st.header("Analysis Settings")
col1, col2 = st.columns(2)

with col1:
    min_occurrences = st.slider("Minimum occurrences per script", min_value=2, max_value=15, value=3)

with col2:
    # Fixed min_scripts_for_common input - using number input instead of slider to avoid errors
    min_scripts_for_common = 2
    st.number_input("Minimum scripts for common keywords", 
                    min_value=2, 
                    max_value=10,
                    value=2,
                    key="min_scripts")

# Submit button in its own row
submitted = st.button("Analyze All Scripts", type="primary")

# Process scripts when the button is clicked
if submitted:
    # Filter out empty scripts
    valid_scripts = [s for s in script_texts if s.strip()]
    
    if not valid_scripts:
        st.error("Please enter at least one script to analyze.")
    else:
        # Analyze each script
        all_results = []
        all_keyword_counts = []
        
        with st.spinner("Analyzing scripts..."):
            for i, script in enumerate(valid_scripts):
                keywords, word_counts = analyze_keywords(script, min_occurrences)
                all_results.append({
                    "script_num": i + 1,
                    "keywords": keywords,
                    "word_count": len(script.split())
                })
                all_keyword_counts.append(word_counts)
            
            # Get min_scripts_for_common from the number input
            min_scripts_for_common = st.session_state.min_scripts
            
            # Find common keywords across scripts
            if len(valid_scripts) > 1:
                common_keywords = find_common_keywords(
                    all_keyword_counts, 
                    min_scripts_for_common, 
                    min_occurrences
                )
            else:
                common_keywords = {}
        
        # Display results in tabs
        if len(valid_scripts) > 1:
            result_tabs = st.tabs(["Common Keywords"] + [f"Script {i+1}" for i in range(len(valid_scripts))])
            
            # Tab for common keywords
            with result_tabs[0]:
                st.header(f"Keywords Common to at least {min_scripts_for_common} Scripts")
                
                if common_keywords:
                    st.success(f"Found {len(common_keywords)} keywords that appear in at least {min_scripts_for_common} scripts with {min_occurrences}+ occurrences each.")
                    
                    # Create dataframe for display
                    common_df = pd.DataFrame({
                        "Keyword": list(common_keywords.keys()),
                        "Total Occurrences": list(common_keywords.values())
                    })
                    
                    # Show bar chart for top 15 keywords
                    st.subheader("Top Common Keywords")
                    top_n = min(15, len(common_keywords))
                    top_common = dict(list(common_keywords.items())[:top_n])
                    
                    chart_data = pd.DataFrame({
                        "Keyword": list(top_common.keys()),
                        "Total Occurrences": list(top_common.values())
                    })
                    
                    st.bar_chart(data=chart_data, x="Keyword", y="Total Occurrences", use_container_width=True)
                    
                    # Display full table
                    st.subheader("All Common Keywords")
                    st.dataframe(common_df, use_container_width=True)
                    
                    # Download option
                    st.download_button(
                        label="Download Common Keywords as CSV",
                        data=common_df.to_csv(index=False).encode('utf-8'),
                        file_name='common_keywords.csv',
                        mime='text/csv',
                    )
                else:
                    st.warning(f"No keywords found that appear in at least {min_scripts_for_common} scripts with {min_occurrences}+ occurrences each. Try lowering the thresholds.")
            
            # Individual script tabs
            for i, result in enumerate(all_results):
                with result_tabs[i+1]:
                    st.header(f"Analysis for Script {result['script_num']}")
                    
                    if result['keywords']:
                        st.success(f"Found {len(result['keywords'])} keywords that appear at least {min_occurrences} times in a script of {result['word_count']} words.")
                        
                        # Create dataframe for display
                        keywords_df = pd.DataFrame({
                            "Keyword": list(result['keywords'].keys()),
                            "Occurrences": list(result['keywords'].values()),
                            "Percentage": [f"{(count / result['word_count'] * 100):.2f}%" for count in result['keywords'].values()]
                        })
                        
                        # Show bar chart
                        st.subheader("Top Keywords")
                        top_n = min(15, len(result['keywords']))
                        top_keywords = dict(list(result['keywords'].items())[:top_n])
                        
                        chart_data = pd.DataFrame({
                            "Keyword": list(top_keywords.keys()),
                            "Occurrences": list(top_keywords.values())
                        })
                        
                        st.bar_chart(data=chart_data, x="Keyword", y="Occurrences", use_container_width=True)
                        
                        # Display full table
                        st.subheader("All Keywords")
                        st.dataframe(keywords_df, use_container_width=True)
                    else:
                        st.warning(f"No keywords found that appear at least {min_occurrences} times. Try lowering the minimum occurrences.")
        else:
            # Single script analysis
            result = all_results[0]
            
            if result['keywords']:
                st.success(f"Found {len(result['keywords'])} keywords that appear at least {min_occurrences} times in a script of {result['word_count']} words.")
                
                # Create dataframe for display
                keywords_df = pd.DataFrame({
                    "Keyword": list(result['keywords'].keys()),
                    "Occurrences": list(result['keywords'].values()),
                    "Percentage": [f"{(count / result['word_count'] * 100):.2f}%" for count in result['keywords'].values()]
                })
                
                # Show bar chart
                st.subheader("Top Keywords")
                top_n = min(15, len(result['keywords']))
                top_keywords = dict(list(result['keywords'].items())[:top_n])
                
                chart_data = pd.DataFrame({
                    "Keyword": list(top_keywords.keys()),
                    "Occurrences": list(top_keywords.values())
                })
                
                st.bar_chart(data=chart_data, x="Keyword", y="Occurrences", use_container_width=True)
                
                # Display full table
                st.subheader("All Keywords")
                st.dataframe(keywords_df, use_container_width=True)
                
                # Download option
                st.download_button(
                    label="Download Keywords as CSV",
                    data=keywords_df.to_csv(index=False).encode('utf-8'),
                    file_name='keywords.csv',
                    mime='text/csv',
                )
            else:
                st.warning(f"No keywords found that appear at least {min_occurrences} times. Try lowering the minimum occurrences.")

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
    
    ## Using Common Keywords Analysis:
    
    If you analyzed multiple successful videos:
    
    1. **Content Strategy**: Create more content around the common keywords
    2. **Playlist Creation**: Group videos with similar keywords into playlists
    3. **Audience Analysis**: Understand what topics resonate across your content
    4. **Competitive Edge**: These keywords likely represent your channel's niche or specialty
    
    Remember that YouTube's algorithm looks for **relevance**, **consistency**, and **viewer engagement**. Keywords are just one part of the equation!
    """)

# Add footer
st.markdown("---")
st.markdown("Created with ❤️ using Streamlit")

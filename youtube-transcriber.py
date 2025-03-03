import os
import re
import sys
import argparse
from collections import Counter
import json
from urllib.parse import urlparse, parse_qs
import language_tool_python
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi

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

def main():
    parser = argparse.ArgumentParser(description='YouTube Transcript Analyzer')
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('-m', '--min-occurrences', type=int, default=3, 
                        help='Minimum number of occurrences for keyword analysis (default: 3)')
    parser.add_argument('-o', '--output', choices=['text', 'json'], default='text',
                        help='Output format (default: text)')
    parser.add_argument('-f', '--file', help='Output file (default: print to console)')
    
    args = parser.parse_args()
    
    transcriber = YouTubeTranscriber()
    result = transcriber.process_video(args.url, args.min_occurrences, args.output)
    
    if args.file:
        with open(args.file, 'w', encoding='utf-8') as f:
            if args.output == 'json':
                json.dump(result, f, ensure_ascii=False, indent=2)
            else:
                f.write(result)
        print(f"Results saved to {args.file}")
    else:
        if args.output == 'json':
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result)

if __name__ == '__main__':
    main()

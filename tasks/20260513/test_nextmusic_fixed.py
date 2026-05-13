"""
Test script for NextMusicTool with AES-GCM encryption
"""
import json
import logging
from tool_next_music_v2 import NextMusicToolV2

# Set logging level to DEBUG
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')

def test_next_music_tool():
    """Test the NextMusicTool with a sample song ID"""
    print("=" * 60)
    print("Testing NextMusicTool with AES-GCM encryption")
    print("=" * 60)
    
    # Initialize the tool
    tool = NextMusicToolV2()
    
    # Test with a song ID from the log
    song_id = "2718994102"
    level = "lossless"
    
    print(f"\nSong ID: {song_id}")
    print(f"Quality Level: {level}")
    print("-" * 60)
    
    try:
        # Get song URL
        result = tool.get_song_url(song_id, level)
        
        print("\nResponse:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get('code') == 200 and result.get('data'):
            data = result['data']
            print("\n" + "=" * 60)
            print("SUCCESS!")
            print("=" * 60)
            print(f"Song Name: {data.get('name', 'N/A')}")
            print(f"Artist: {data.get('singer', 'N/A')}")
            print(f"Album: {data.get('album', 'N/A')}")
            print(f"Quality: {data.get('level', 'N/A')}")
            print(f"Size: {data.get('size', 'N/A')}")
            print(f"URL: {data.get('url', 'N/A')[:100]}...")
        else:
            print("\n" + "=" * 60)
            print("FAILED!")
            print("=" * 60)
            print(f"Error: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_next_music_tool()

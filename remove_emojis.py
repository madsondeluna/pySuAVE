#!/usr/bin/env python3
"""Remove all emojis from markdown files."""

import re
from pathlib import Path

def remove_emojis(text):
    """Remove all emoji characters from text."""
    # Comprehensive emoji pattern covering all Unicode emoji ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA00-\U0001FA6F"  # chess symbols
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "\U00002700-\U000027BF"  # dingbats
        "\u2600-\u26FF"          # miscellaneous symbols
        "\u2700-\u27BF"          # dingbats
        "\u2300-\u23FF"          # miscellaneous technical
        "\u2B50"                 # star
        "\u2705"                 # check mark
        "\u274C"                 # cross mark
        "\u2714"                 # heavy check mark
        "\u2716"                 # heavy multiplication x
        "\u271D"                 # latin cross
        "\u2721"                 # star of david
        "\u2728"                 # sparkles
        "\u2733"                 # eight spoked asterisk
        "\u2734"                 # eight pointed black star
        "\u2744"                 # snowflake
        "\u2747"                 # sparkle
        "\u274E"                 # negative squared cross mark
        "\u2753"                 # question mark
        "\u2754"                 # white question mark
        "\u2755"                 # white exclamation mark
        "\u2757"                 # exclamation mark
        "\u2795"                 # heavy plus sign
        "\u2796"                 # heavy minus sign
        "\u2797"                 # heavy division sign
        "\u27A1"                 # black rightwards arrow
        "\u27B0"                 # curly loop
        "\u27BF"                 # double curly loop
        "\u3030"                 # wavy dash
        "\u303D"                 # part alternation mark
        "\u3297"                 # circled ideograph congratulation
        "\u3299"                 # circled ideograph secret
        "]+", 
        flags=re.UNICODE
    )
    
    return emoji_pattern.sub('', text)

def process_file(filepath):
    """Remove emojis from a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned = remove_emojis(content)
        
        if cleaned != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            print(f"Cleaned: {filepath}")
            return True
        else:
            print(f"No emojis found: {filepath}")
            return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Process all markdown files."""
    base_path = Path('.')
    md_files = list(base_path.rglob('*.md'))
    
    # Exclude .git directory
    md_files = [f for f in md_files if '.git' not in str(f)]
    
    print(f"Found {len(md_files)} markdown files")
    print("=" * 60)
    
    cleaned_count = 0
    for md_file in md_files:
        if process_file(md_file):
            cleaned_count += 1
    
    print("=" * 60)
    print(f"Cleaned {cleaned_count} files")

if __name__ == '__main__':
    main()

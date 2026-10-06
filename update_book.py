import urllib.request
import xml.etree.ElementTree as ET
import re
import os
import sys

# Fetch the URL securely from GitHub Secrets to hide your profile ID
RSS_URL = os.environ.get("GOODREADS_RSS_URL")

if not RSS_URL:
    print("Error: GOODREADS_RSS_URL environment variable not set.")
    sys.exit(1)

try:
    print("Fetching RSS feed...")
    req = urllib.request.Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    
    first_item = root.find('./channel/item')
    if first_item is not None:
        title = first_item.find('title').text
        author = first_item.find('author_name').text
        
        # Extract the public book ID to link to the book page rather than your personal review
        book_id = first_item.find('book_id').text
        book_link = f"https://www.goodreads.com/book/show/{book_id}"
        
        # Clean up CDATA if present and strip whitespace
        title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
        author = author.replace('<![CDATA[', '').replace(']]>', '').strip()
        
        new_text = f"<em><a href=\"{book_link}\" target=\"_blank\">{title}</a></em> by {author}."
        
        # Read the current index.html
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace content between our specific HTML comments
        pattern = r'(<!-- CURRENTLY_READING_START -->)(.*?)(<!-- CURRENTLY_READING_END -->)'
        updated_content = re.sub(pattern, rf'\g<1>{new_text}\g<3>', content, flags=re.DOTALL)
        
        # Write the updated content back
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_content)
            
        print(f"Success! Updated to: {new_text}")
    else:
        print("No books found in the currently reading shelf.")
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)

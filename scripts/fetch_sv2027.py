import requests
from bs4 import BeautifulSoup
import json
import os
import sys
import re

def fetch_sv2027(book, chapter, local=False):
    if local:
        # Support the exact names of the manual downloads
        possible_paths = [
            f"research/Bijbel – Statenvertaling 2027.{book}.{chapter}.html",
            f"research/{book}.{chapter}.raw.html",
            f"research/{book}.{chapter}.html"
        ]
        html_content = None
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Reading local file {path}...")
                with open(path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                break
        
        if not html_content:
            print(f"Error: No local file found for {book} {chapter}.")
            return None
    else:
        # ... (fetch logic remains same)
        url = f"https://statenvertaling2027.nl/bijbel/sv2027/{book}.{chapter}"
        print(f"Fetching {url}...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200: return None
            html_content = r.text
        except: return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    container = soup.find('div', class_='scripture_container')
    if not container:
        print("Error: Could not find scripture_container.")
        return None

    # Group everything by verse number using the 'rel' attribute
    verse_map = {} # verse_num -> string
    
    # First, find all collapse divs (footnotes/refs) and map them by ID
    collapses = {}
    for div in soup.find_all('div', class_='collapse'):
        cid = div.get('id')
        if not cid: continue
        
        body = div.find('div', class_='modal-body')
        if not body: continue
        
        if 'footnote' in cid:
            # Format: <lemma - note>
            # The structure is often: <span fq>lemma</span><span> - note</span>
            text = body.get_text(separator=" ").strip()
            # Clean up: "lemma – note" -> "<lemma – note>"
            collapses[cid] = f" <{text}> "
        elif 'cross' in cid:
            # Format: $ref. 1, ref. 2$
            refs = [a.get_text().strip() for a in body.find_all('a')]
            if refs:
                collapses[cid] = f" ${'; '.join(refs)}$ "

    # Process all verse-spans
    for span in container.find_all('span', class_='verse-span'):
        rel = span.get('rel', '')
        if not rel or not isinstance(rel, str): continue
        
        # rel is usually like "LUK.1.1 "
        m = re.search(r'\.(\d+)\s*$', rel)
        if not m: continue
        v_num = int(m.group(1))
        
        if v_num not in verse_map:
            verse_map[v_num] = ""
        
        if 'verse_footnote' in span.get('class', []):
            target = span.get('data-bs-target', '').replace('#', '')
            if target in collapses:
                verse_map[v_num] += collapses[target]
        else:
            # Get text, but skip the verse number itself if it's the number span
            if 'verse_number' in span.get('class', []):
                continue
            
            # Use get_text to get nested verse_text
            text = span.get_text().strip()
            if text:
                verse_map[v_num] += text + " "

    # Extract all headers as introduction summary
    headers = [h.get_text().strip() for h in container.find_all('div', class_='heading')]
    
    data = {
        "book": book,
        "chapter": int(chapter),
        "introduction": {
            "modernized": " | ".join(headers)
        },
        "verses": []
    }
    
    for v_num in sorted(verse_map.keys()):
        text = re.sub(r'\s+', ' ', verse_map[v_num]).strip()
        data["verses"].append({
            "verse_number": v_num,
            "modernized": text
        })
        
    return data

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("book", nargs="?", default="LUK")
    parser.add_argument("chapter", nargs="?", default="1")
    parser.add_argument("--local", action="store_true", help="Read from research/{book}.{chapter}.raw.html instead of fetching")
    args = parser.parse_args()
    
    result = fetch_sv2027(args.book, args.chapter, local=args.local)
    if result:
        output_dir = f"initiatiefsv27/{args.book}"
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/{args.book}.{args.chapter}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully saved to {output_path}")

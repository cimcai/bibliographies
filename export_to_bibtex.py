#!/usr/bin/env python3
"""
Convert markdown bibliography files to BibTeX format.
"""

import re
import os
from pathlib import Path
from urllib.parse import urlparse

def extract_doi(url):
    """Extract DOI from URL."""
    if url:
        if 'doi.org' in url or 'doi:' in url.lower():
            match = re.search(r'10\.\d+/[^\s\)]+', url)
            if match:
                return match.group(0)
    return None

def generate_bibtex_key(authors, year, title):
    """Generate a BibTeX key from author, year, and title."""
    # Get first author's last name
    if authors:
        first_author = authors[0].split(',')[0].strip()
        last_name = first_author.split()[-1] if first_author.split() else first_author
    else:
        last_name = "Unknown"
    
    # Get first significant word from title
    title_words = re.findall(r'\b\w+\b', title.lower())
    first_word = title_words[0] if title_words else "unknown"
    
    return f"{last_name}{year}{first_word.capitalize()}"

def parse_citation(line):
    """Parse a citation line and extract components."""
    # Remove markdown bullet points
    line = re.sub(r'^[-*]\s+', '', line.strip())
    if not line:
        return None
    
    # Extract URL/DOI if present
    url_match = re.search(r'(https?://[^\s]+|doi\.org/[^\s]+)', line)
    url = url_match.group(0) if url_match else None
    if url_match:
        line = line[:url_match.start()].strip()
    
    # Extract year
    year_match = re.search(r'\((\d{4}(?:–\d{4})?)\)', line)
    year = year_match.group(1) if year_match else None
    if year:
        year = year.split('–')[0]  # Take first year if range
    
    # Extract authors (everything before the year)
    if year_match:
        authors_part = line[:year_match.start()].strip()
    else:
        authors_part = line.split('.')[0] if '.' in line else ""
    
    # Parse authors - handle "&" and "and"
    authors = []
    if authors_part:
        # Replace "and" with "&" for consistency
        authors_text = re.sub(r'\s+and\s+', ' & ', authors_part, flags=re.IGNORECASE)
        # Split on commas, but preserve "&" groups
        parts = re.split(r',\s*(?=[A-Z][a-z]+(?:\s+[A-Z]\.?)*\s*&)', authors_text)
        for part in parts:
            # Handle "&" separated authors
            if '&' in part:
                for author in part.split('&'):
                    author = author.strip()
                    if author:
                        authors.append(author)
            else:
                author = part.strip()
                if author:
                    authors.append(author)
    
    # Extract the rest after year
    if year_match:
        rest = line[year_match.end():].strip()
    else:
        rest = line
    
    # Remove leading period
    rest = re.sub(r'^\.\s*', '', rest)
    
    # Check for "In" pattern (chapter in book)
    in_match = re.search(r'\.\s+In\s+([^.]+)\.', rest, re.IGNORECASE)
    is_chapter = bool(in_match)
    
    # Extract title - look for text before italicized journal or before "In"
    title = None
    journal = None
    publisher = None
    volume = None
    issue = None
    pages = None
    editors = None
    
    if is_chapter:
        # Chapter in book: "Title. In Editor (Ed.), Book Title (pp. X-Y). Publisher"
        title_match = re.match(r'^([^.]+)\.', rest)
        if title_match:
            title = title_match.group(1).strip()
            rest = rest[len(title_match.group(0)):].strip()
        
        # Extract editor and book title
        editor_match = re.search(r'In\s+([^(]+)\s*\(Eds?\.\)', rest, re.IGNORECASE)
        if editor_match:
            editors_text = editor_match.group(1).strip()
            # Parse editors similar to authors
            editors = []
            editors_text = re.sub(r'\s+and\s+', ' & ', editors_text, flags=re.IGNORECASE)
            parts = re.split(r',\s*(?=[A-Z][a-z]+(?:\s+[A-Z]\.?)*\s*&)', editors_text)
            for part in parts:
                if '&' in part:
                    for editor in part.split('&'):
                        editor = editor.strip()
                        if editor:
                            editors.append(editor)
                else:
                    editor = part.strip()
                    if editor:
                        editors.append(editor)
            rest = rest[editor_match.end():].strip()
        
        # Extract book title (italicized)
        book_title_match = re.search(r'\*([^*]+)\*', rest)
        if book_title_match:
            journal = book_title_match.group(1).strip()  # Using journal field for book title
            rest = rest.replace(f'*{journal}*', '').strip()
        
        # Extract pages
        pages_match = re.search(r'\(pp\.\s*(\d+)\s*[–-]\s*(\d+)\)', rest)
        if pages_match:
            pages = f"{pages_match.group(1)}--{pages_match.group(2)}"
            rest = rest.replace(pages_match.group(0), '').strip()
        
        # Extract publisher
        publisher_match = re.search(r'([A-Z][^.]*(?:Press|Books|Publishers?|University|MIT|Oxford|Cambridge|Springer|Wiley))', rest)
        if publisher_match:
            publisher = publisher_match.group(1).strip()
    else:
        # Article or book
        # Check if there's an italicized title (book) or italicized journal (article)
        italic_match = re.search(r'\*([^*]+)\*', rest)
        
        if italic_match:
            italic_text = italic_match.group(1).strip()
            italic_start = italic_match.start()
            
            # Text before italic is likely the title
            before_italic = rest[:italic_start].strip()
            if before_italic:
                title = before_italic.rstrip('.').strip()
            
            # Check if italic text looks like a journal (has volume/issue pattern or common journal words)
            journal_pattern = r'\d+.*\d+|Review|Journal|Proceedings|Transactions|Bulletin'
            if re.search(journal_pattern, italic_text, re.IGNORECASE):
                # It's a journal
                journal = italic_text
                # Extract volume and issue from journal string
                vol_issue_match = re.search(r'(\d+)\s*\((\d+)\)', italic_text)
                if vol_issue_match:
                    volume = vol_issue_match.group(1)
                    issue = vol_issue_match.group(2)
                    # Remove volume/issue from journal name
                    journal = re.sub(r'\s*\d+\s*\(\d+\)', '', journal).strip()
                else:
                    # Just volume
                    vol_match = re.search(r',\s*(\d+)', italic_text)
                    if vol_match:
                        volume = vol_match.group(1)
                        journal = re.sub(r',\s*\d+.*$', '', journal).strip()
                
                # Extract pages after journal
                rest_after = rest[italic_match.end():].strip()
                pages_match = re.search(r'(\d+)\s*[–-]\s*(\d+)', rest_after)
                if pages_match:
                    pages = f"{pages_match.group(1)}--{pages_match.group(2)}"
            else:
                # It's a book title
                title = italic_text
                # Extract publisher from rest
                rest_after = rest[italic_match.end():].strip()
                publisher_match = re.search(r'([A-Z][^.]*(?:Press|Books|Publishers?|University|MIT|Oxford|Cambridge|Springer|Wiley))', rest_after)
                if publisher_match:
                    publisher = publisher_match.group(1).strip()
        else:
            # No italic text - try to extract title as first sentence
            title_match = re.match(r'^([^.]+\.[^.]*)', rest)
            if title_match:
                title = title_match.group(1).strip()
            else:
                title = rest.split('.')[0].strip() if rest else None
    
    return {
        'authors': authors,
        'year': year or 'n.d.',
        'title': title,
        'journal': journal,
        'publisher': publisher,
        'volume': volume,
        'issue': issue,
        'pages': pages,
        'url': url,
        'doi': extract_doi(url) if url else None,
        'editors': editors,
        'is_chapter': is_chapter
    }

def format_bibtex_entry(citation, entry_type='article'):
    """Format a citation dictionary as a BibTeX entry."""
    if not citation or not citation.get('title'):
        return None
    
    # Determine entry type
    if citation.get('is_chapter'):
        entry_type = 'incollection'
    elif citation.get('publisher') and not citation.get('journal'):
        entry_type = 'book'
    elif citation.get('journal'):
        entry_type = 'article'
    else:
        entry_type = 'misc'
    
    # Generate key
    key = generate_bibtex_key(
        citation.get('authors', []),
        citation.get('year', 'n.d.'),
        citation.get('title', '')
    )
    
    # Format authors/editors
    authors = ' and '.join(citation.get('authors', []))
    editors = ' and '.join(citation.get('editors', [])) if citation.get('editors') else None
    
    # Build entry
    fields = []
    if authors:
        fields.append(f"  author = {{{authors}}}")
    if editors:
        fields.append(f"  editor = {{{editors}}}")
    if citation.get('year') and citation.get('year') != 'n.d.':
        fields.append(f"  year = {{{citation['year']}}}")
    if citation.get('title'):
        fields.append(f"  title = {{{citation['title']}}}")
    if citation.get('journal'):
        fields.append(f"  journal = {{{citation['journal']}}}")
    if citation.get('publisher'):
        fields.append(f"  publisher = {{{citation['publisher']}}}")
    if citation.get('volume'):
        fields.append(f"  volume = {{{citation['volume']}}}")
    if citation.get('issue'):
        fields.append(f"  number = {{{citation['issue']}}}")
    if citation.get('pages'):
        fields.append(f"  pages = {{{citation['pages']}}}")
    if citation.get('doi'):
        fields.append(f"  doi = {{{citation['doi']}}}")
    elif citation.get('url'):
        fields.append(f"  url = {{{citation['url']}}}")
    
    entry = f"@{entry_type}{{{key},\n" + ',\n'.join(fields) + "\n}"
    return entry

def convert_file_to_bibtex(md_file, output_dir):
    """Convert a markdown bibliography file to BibTeX."""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract citation lines
    lines = content.split('\n')
    citations = []
    
    for line in lines:
        # Skip headers and separators
        if line.startswith('#') or line.startswith('---') or not line.strip():
            continue
        
        # Check if it's a citation line
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            citation = parse_citation(line)
            if citation:
                citations.append(citation)
    
    # Generate BibTeX file
    bibtex_entries = []
    for citation in citations:
        entry = format_bibtex_entry(citation)
        if entry:
            bibtex_entries.append(entry)
    
    if bibtex_entries:
        # Create output filename
        md_name = Path(md_file).stem
        output_file = output_dir / f"{md_name}.bib"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(bibtex_entries))
        
        print(f"Converted {md_file} -> {output_file} ({len(bibtex_entries)} entries)")
        return len(bibtex_entries)
    
    return 0

def main():
    """Main function to convert all bibliography files."""
    base_dir = Path(__file__).parent
    output_dir = base_dir / 'bibtex'
    output_dir.mkdir(exist_ok=True)
    
    total_entries = 0
    
    # Convert files in general/
    general_dir = base_dir / 'general'
    if general_dir.exists():
        for md_file in general_dir.glob('*.md'):
            total_entries += convert_file_to_bibtex(md_file, output_dir)
    
    # Convert files in seminar/
    seminar_dir = base_dir / 'seminar'
    if seminar_dir.exists():
        for md_file in seminar_dir.glob('*.md'):
            total_entries += convert_file_to_bibtex(md_file, output_dir)
    
    # Convert files in library/
    library_dir = base_dir / 'library'
    if library_dir.exists():
        for md_file in library_dir.glob('*.md'):
            total_entries += convert_file_to_bibtex(md_file, output_dir)
    
    print(f"\nTotal: {total_entries} BibTeX entries created in {output_dir}/")

if __name__ == '__main__':
    main()

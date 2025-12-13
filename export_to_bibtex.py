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
    
    # Pattern for APA-style citations
    # Author(s). (Year). Title. Journal/Publisher. DOI/URL
    
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
    
    # Parse authors
    authors = []
    if authors_part:
        # Handle "&" and "and" separators
        authors_text = re.sub(r'\s+and\s+', ' & ', authors_part, flags=re.IGNORECASE)
        author_list = re.split(r',\s*(?=[A-Z][a-z]+(?:\s+[A-Z]\.?)*\s+&)', authors_text)
        for author in author_list:
            author = author.replace('&', '').strip()
            if author:
                authors.append(author)
    
    # Extract title (between year and period before journal/publisher)
    if year_match:
        rest = line[year_match.end():].strip()
    else:
        rest = line
    
    # Remove leading period
    rest = re.sub(r'^\.\s*', '', rest)
    
    # Check if it's a book (italicized title) or article
    title_match = re.search(r'\*([^*]+)\*', rest)
    if title_match:
        title = title_match.group(1).strip()
        # Remove title from rest
        rest = rest.replace(f'*{title}*', '').strip()
    else:
        # No italicized title, try to extract first sentence
        title_match = re.match(r'^([^.]+\.[^.]*)', rest)
        title = title_match.group(1).strip() if title_match else rest.split('.')[0].strip()
        rest = rest[len(title):].strip() if title_match else rest
    
    # Extract journal/publisher
    journal = None
    publisher = None
    volume = None
    pages = None
    
    # Look for journal patterns
    journal_match = re.search(r'\*([^*]+)\*', rest)
    if journal_match:
        journal = journal_match.group(1).strip()
        rest = rest.replace(f'*{journal}*', '').strip()
    
    # Look for volume and pages
    vol_match = re.search(r'(\d+)\s*\((\d+)\)', rest)
    if vol_match:
        volume = vol_match.group(1)
        rest = rest.replace(vol_match.group(0), '').strip()
    
    pages_match = re.search(r'(\d+)\s*[–-]\s*(\d+)', rest)
    if pages_match:
        pages = f"{pages_match.group(1)}--{pages_match.group(2)}"
    
    # If no journal, might be a book with publisher
    if not journal and rest:
        publisher_match = re.search(r'([A-Z][^.]*(?:Press|Books|Publishers?|University|MIT|Oxford|Cambridge|Springer|Wiley))', rest)
        if publisher_match:
            publisher = publisher_match.group(1).strip()
    
    return {
        'authors': authors,
        'year': year or 'n.d.',
        'title': title,
        'journal': journal,
        'publisher': publisher,
        'volume': volume,
        'pages': pages,
        'url': url,
        'doi': extract_doi(url) if url else None
    }

def format_bibtex_entry(citation, entry_type='article'):
    """Format a citation dictionary as a BibTeX entry."""
    if not citation or not citation.get('title'):
        return None
    
    # Determine entry type
    if citation.get('publisher') and not citation.get('journal'):
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
    
    # Format authors
    authors = ' and '.join(citation.get('authors', []))
    
    # Build entry
    fields = []
    if authors:
        fields.append(f"  author = {{{authors}}}")
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



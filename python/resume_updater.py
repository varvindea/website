"""
Resume Updater Class
Converts resume content from text file to HTML format
Keeps the styling consistent while updating content from a single source of truth (txt file)
"""

class ResumeUpdater:
    def __init__(self, txt_file_path, html_file_path):
        import os
        self.txt_file = os.path.abspath(txt_file_path)
        self.html_file = os.path.abspath(html_file_path)
        self.resume_data = {}

    def parse_text_resume(self):
        content = None
        for encoding in ['utf-8-sig', 'utf-8', 'latin-1']:
            try:
                with open(self.txt_file, 'r', encoding=encoding) as f:
                    content = f.read()
                if content.strip():
                    break
            except Exception:
                continue

        if not content or not content.strip():
            raise Exception(f"Could not read file: {self.txt_file}")

        content = content.replace('\u2011', '-').replace('\u2013', '–').replace('\u2014', '—')

        lines = [line.rstrip() for line in content.split('\n') if line.strip()]

        self.resume_data['name'] = lines[0].strip() if lines else ''

        # Title may be wrapped across two lines (PDF extraction artifact)
        title = lines[1].strip() if len(lines) > 1 else ''
        title_end = 1
        if len(lines) > 2:
            nxt = lines[2].strip()
            section_starts = ('EXPERIENCE', 'SKILLS', 'WORK', 'Education', 'Certification')
            if not any(nxt.startswith(s) for s in section_starts) and '@' not in nxt and not nxt[0].isdigit():
                title = title.rstrip('|').rstrip() + ' ' + nxt
                title_end = 2
        self.resume_data['title'] = title

        # Contact line may also be wrapped (line ending with '|')
        contact_text = ''
        for i in range(title_end + 1, min(title_end + 4, len(lines))):
            line = lines[i].strip()
            if '|' in line or '@' in line:
                contact_text = line
                if contact_text.endswith('|') and i + 1 < len(lines):
                    contact_text = contact_text + ' ' + lines[i + 1].strip()
                break
        self.resume_data['contact'] = [p.strip() for p in contact_text.split('|') if p.strip()] or ['Resume provided']

        self.resume_data['sections'] = self._extract_sections(content)
        return self.resume_data

    def _extract_sections(self, content):
        # Section headers as they appear in PDF-extracted text
        markers = [
            'EXPERIENCE SUMMARY',
            'SKILLS & EXPERTISE',
            'WORK EXPERIENCE:',
            'WORK EXPERIENCE',
            'Education',
            'Certification',
        ]

        found = {}
        for marker in markers:
            pos = content.find(marker)
            if pos != -1 and marker not in found:
                found[marker] = pos

        sorted_markers = sorted(found.items(), key=lambda x: x[1])

        sections = {}
        for i, (name, pos) in enumerate(sorted_markers):
            start = pos + len(name)
            end = sorted_markers[i + 1][1] if i + 1 < len(sorted_markers) else len(content)
            key = name.rstrip(':')
            sections[key] = content[start:end].strip().lstrip(':').strip()

        return sections

    def _parse_bullets_and_headers(self, lines):
        """Return list of ('bullet'|'subheader', text) tuples, joining PDF-wrapped lines."""
        result = []
        current_bullet = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('●') or line.startswith('•'):
                if current_bullet is not None:
                    result.append(('bullet', current_bullet.strip()))
                current_bullet = line.lstrip('●•').strip()
            elif current_bullet is not None:
                # Continuation if the bullet text doesn't yet end a sentence
                if not current_bullet.endswith(('.', '!', '?')):
                    current_bullet += ' ' + line
                else:
                    result.append(('bullet', current_bullet.strip()))
                    current_bullet = None
                    result.append(('subheader', line))
            else:
                result.append(('subheader', line))

        if current_bullet is not None:
            result.append(('bullet', current_bullet.strip()))

        return result
    
    def generate_html(self):
        self.parse_text_resume()

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.resume_data['name']} - Resume</title>
    <style>
        :root {{
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --text-color: #333;
            --background-color: #f5f6fa;
            --section-bg: #ffffff;
            --light-accent: #ecf0f1;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--section-bg);
            padding: 40px;
            max-width: 1000px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 2px solid var(--background-color);
        }}

        h1 {{
            color: var(--primary-color);
            font-size: 28px;
            margin-bottom: 0.5rem;
        }}

        h2 {{
            color: var(--secondary-color);
            font-size: 20px;
            margin-bottom: 1rem;
        }}

        .contact-info {{
            margin-top: 1rem;
            color: var(--primary-color);
            font-size: 14px;
        }}

        .contact-info a {{
            color: var(--secondary-color);
            text-decoration: none;
        }}

        .contact-info a:hover {{
            text-decoration: underline;
        }}

        section {{
            margin-bottom: 2rem;
        }}

        section h2 {{
            color: var(--primary-color);
            font-size: 20px;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--background-color);
        }}

        .summary {{
            background-color: var(--light-accent);
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            line-height: 1.8;
        }}

        .expertise-grid {{
            display: grid;
            grid-template-columns: repeat(1, 1fr);
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .expertise-item {{
            background-color: var(--light-accent);
            padding: 1.5rem;
            border-radius: 8px;
        }}

        .expertise-item h3 {{
            color: var(--primary-color);
            font-size: 16px;
            margin-bottom: 0.8rem;
            padding-bottom: 0.3rem;
            border-bottom: 1px solid rgba(52, 152, 219, 0.2);
        }}

        .expertise-item p {{
            line-height: 1.7;
        }}

        .job {{
            margin-bottom: 2rem;
            page-break-inside: avoid;
        }}

        .job h3 {{
            color: var(--primary-color);
            font-size: 18px;
            margin-bottom: 0.3rem;
        }}

        .job-meta {{
            color: #666;
            font-style: italic;
            font-size: 14px;
            margin-bottom: 0.8rem;
        }}

        .job ul {{
            list-style: none;
            margin: 0.8rem 0;
        }}

        .job li {{
            margin-bottom: 0.6rem;
            padding-left: 1.2rem;
            position: relative;
        }}

        .job li::before {{
            content: "▹";
            color: var(--secondary-color);
            position: absolute;
            left: 0;
        }}

        .job h4 {{
            color: var(--secondary-color);
            font-size: 15px;
            margin: 1rem 0 0.5rem;
            font-weight: 600;
        }}

        .education {{
            page-break-inside: avoid;
        }}

        .degree {{
            margin-bottom: 1.5rem;
        }}

        .degree h3 {{
            color: var(--secondary-color);
            font-size: 16px;
            margin-bottom: 0.3rem;
        }}

        .degree p {{
            color: #666;
            font-size: 14px;
            margin: 0.2rem 0;
        }}

        .certification {{
            page-break-inside: avoid;
        }}

        .cert-item {{
            margin-bottom: 1rem;
            padding-left: 1.2rem;
            position: relative;
        }}

        .cert-item::before {{
            content: "✓";
            color: var(--secondary-color);
            position: absolute;
            left: 0;
            font-weight: bold;
        }}

        @media print {{
            body {{
                padding: 20px;
                background: white;
            }}

            .expertise-grid {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>{self.resume_data['name']}</h1>
        <h2>{self.resume_data['title']}</h2>
        <div class="contact-info">
            {' | '.join(self.resume_data['contact'])}
        </div>
    </header>

    {self._generate_summary_section()}
    {self._generate_skills_section()}
    {self._generate_experience_section()}
    {self._generate_education_section()}
    {self._generate_certification_section()}

</body>
</html>"""
        
        return html_content

    def _generate_summary_section(self):
        summary = self.resume_data['sections'].get('EXPERIENCE SUMMARY', '')
        if not summary:
            return ''
        return f'<section class="summary"><p>{summary.strip()}</p></section>'

    def _generate_skills_section(self):
        skills_text = self.resume_data['sections'].get('SKILLS & EXPERTISE', '')
        if not skills_text:
            return ''

        # Each category is "Category Name: content..." possibly wrapped across lines
        import re
        categories = {}
        current_cat = None
        current_content = []

        for line in skills_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            # New category: line starts with "Word(s): " pattern
            match = re.match(r'^([A-Z][^:]{2,50}):\s*(.*)', line)
            if match:
                if current_cat:
                    categories[current_cat] = ' '.join(current_content)
                current_cat = match.group(1)
                current_content = [match.group(2)] if match.group(2) else []
            elif current_cat:
                current_content.append(line)

        if current_cat:
            categories[current_cat] = ' '.join(current_content)

        html = '<section class="technical-expertise"><h2>Skills &amp; Expertise</h2><div class="expertise-grid">'
        for category, text in categories.items():
            html += f'<div class="expertise-item"><h3>{category}</h3><p>{text}</p></div>'
        html += '</div></section>'
        return html

    def _generate_experience_section(self):
        exp_text = self.resume_data['sections'].get('WORK EXPERIENCE', '')
        if not exp_text:
            return ''

        # Split into individual job blocks on the "Work Experience: Previous Employer" separator
        job_blocks_raw = exp_text.split('Work Experience: Previous Employer')
        html = '<section class="experience"><h2>Professional Experience</h2>'

        for block in job_blocks_raw:
            lines = [l for l in block.split('\n') if l.strip()]
            if not lines:
                continue

            # Split header (before first bullet) from content
            first_bullet = next((i for i, l in enumerate(lines) if l.strip().startswith(('●', '•'))), len(lines))
            header_lines = [l.strip() for l in lines[:first_bullet]]
            content_lines = lines[first_bullet:]

            # Parse header: first 1-2 lines = title+dates, then company
            title = ''
            company = ''
            if header_lines:
                # Detect if the title wraps (ends with – or 'to')
                title = header_lines[0]
                idx = 1
                if idx < len(header_lines):
                    nxt = header_lines[idx]
                    # Continuation: pure date or "Present"
                    if nxt in ('Present',) or (len(nxt) < 15 and any(c.isdigit() for c in nxt)):
                        title += ' ' + nxt
                        idx += 1
                if idx < len(header_lines):
                    company = header_lines[idx]

            # Strip "Key Contributions:" label that appears in older roles
            content_lines = [l for l in content_lines if l.strip() != 'Key Contributions:']

            parsed = self._parse_bullets_and_headers(content_lines)

            html += '<div class="job">'
            if title:
                # Split title from company/location if in same line (older roles use –)
                if '–' in title and not company:
                    parts = title.split('–', 1)
                    html += f'<h3>{parts[0].strip()}</h3>'
                    html += f'<div class="job-meta">{parts[1].strip()}</div>'
                else:
                    html += f'<h3>{title}</h3>'
                    if company:
                        html += f'<div class="job-meta">{company}</div>'

            for kind, text in parsed:
                if kind == 'subheader':
                    html += f'<h4>{text}</h4>'
                elif kind == 'bullet':
                    html += f'<ul><li>{text}</li></ul>'

            html += '</div>'

        html += '</section>'
        return html

    def _generate_education_section(self):
        edu_text = self.resume_data['sections'].get('Education', '')
        if not edu_text:
            return ''

        lines = [l for l in edu_text.split('\n') if l.strip()]
        parsed = self._parse_bullets_and_headers(lines)

        html = '<section class="education"><h2>Education</h2>'
        for kind, text in parsed:
            if kind == 'bullet':
                html += f'<div class="degree"><p>{text}</p></div>'
        html += '</section>'
        return html

    def _generate_certification_section(self):
        cert_text = self.resume_data['sections'].get('Certification', '')
        if not cert_text:
            return ''

        lines = [l for l in cert_text.split('\n') if l.strip()]
        parsed = self._parse_bullets_and_headers(lines)

        html = '<section class="certification"><h2>Certifications</h2>'
        for kind, text in parsed:
            if kind == 'bullet':
                html += f'<div class="cert-item">{text}</div>'
        html += '</section>'
        return html

    def update_html_file(self):
        html_content = self.generate_html()
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ Resume updated successfully: {self.html_file}")

    def run(self):
        try:
            self.update_html_file()
            return True
        except Exception as e:
            print(f"✗ Error updating resume: {str(e)}")
            return False


if __name__ == "__main__":
    import sys
    import os
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up one level to find the html folder
    parent_dir = os.path.dirname(script_dir)
    
    # Configuration - paths relative to parent directory
    txt_file = os.path.join(parent_dir, "html", "raw-resum-Aug162026.txt")
    html_file = os.path.join(parent_dir, "html", "resume-pdf.html")
    
    # Run the updater
    updater = ResumeUpdater(txt_file, html_file)
    success = updater.run()
    
    sys.exit(0 if success else 1)

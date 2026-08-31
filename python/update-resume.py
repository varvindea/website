#!/usr/bin/env python3
"""
Resume Updater Helper Script
Provides easy interface to update and validate resume
Updated to work with new folder structure (python/ and html/)
"""

import os
import sys
from pathlib import Path
from resume_updater import ResumeUpdater


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def main():
    """Main helper function"""
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up one level to find the html folder
    parent_dir = os.path.dirname(script_dir)
    
    # Configuration - paths relative to parent directory
    txt_file = os.path.join(parent_dir, "html", "raw-resum-Aug162026.txt")
    html_file = os.path.join(parent_dir, "html", "resume-pdf.html")
    
    # Check if files exist
    if not os.path.exists(txt_file):
        print(f"❌ Error: Cannot find '{txt_file}'")
        return False
    
    print_header("Resume Updater")
    
    # Parse and display info
    print(f"📄 Reading resume from: {txt_file}")
    updater = ResumeUpdater(txt_file, html_file)
    
    try:
        data = updater.parse_text_resume()
        
        print(f"✓ Name: {data['name']}")
        print(f"✓ Title: {data['title']}")
        print(f"✓ Contact: {len(data['contact'])} contact methods")
        
        sections = data['sections']
        print(f"\n✓ Sections found:")
        for section_name in sections.keys():
            char_count = len(sections[section_name])
            print(f"  • {section_name}: {char_count} characters")
        
        # Generate HTML
        print(f"\n📝 Generating HTML resume...")
        updater.update_html_file()
        
        # Verify output
        if os.path.exists(html_file):
            file_size = os.path.getsize(html_file)
            print(f"✓ HTML file created: {html_file} ({file_size} bytes)")
            print_header("Resume Updated Successfully!")
            print(f"📋 Open {html_file} in your browser to view")
            return True
        else:
            print(f"❌ Error: HTML file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

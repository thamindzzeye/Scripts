import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse
from pathlib import Path
import mimetypes
import time
from fpdf import FPDF
from PIL import Image

class WebsiteMediaScraper:
    def __init__(self):
        # Set downloads directory
        self.download_dir = Path.home() / "Downloads" / "Website_Media"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Track visited URLs and downloaded images
        self.visited_urls = set()
        self.image_map = {}  # Maps original URLs to local filenames
        
        # Supported media types
        self.image_types = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
        self.video_types = ('.mp4', '.webm', '.avi', '.mov', '.wmv', '.mkv')
        self.pdf_types = ('.pdf',)
        
        # Cancellation flag
        self.is_cancelled = False

    def is_media_file(self, url):
        """Check if URL points to a supported media file (including PDFs)"""
        path = urlparse(url).path.lower()
        return path.endswith(self.image_types + self.video_types + self.pdf_types)

    def is_element_visible(self, element):
        """Check if an element is likely visible based on common attributes and styles"""
        if element.get('hidden') is not None:
            return False
        
        style = element.get('style', '').lower()
        if 'display: none' in style or 'visibility: hidden' in style:
            return False
            
        if 'width: 0' in style or 'height: 0' in style:
            return False
            
        parent = element.parent
        while parent and parent.name != 'body':
            if parent.get('hidden') is not None:
                return False
            parent_style = parent.get('style', '').lower()
            if 'display: none' in parent_style or 'visibility: hidden' in parent_style:
                return False
            parent = parent.parent
            
        return True

    def download_file(self, url, filename, is_image=False):
        """Download a file and optionally track it if it's an image"""
        try:
            filepath = self.download_dir / filename
            
            # Skip if file already exists
            if filepath.exists():
                if is_image:
                    self.image_map[url] = filename  # Still map it for reference
                print(f"Skipping existing file: {filename}")
                return
            
            # Download the file
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self.is_cancelled:
                        print(f"Cancelled download of {filename}")
                        return
                    f.write(chunk)
            
            if is_image:
                self.image_map[url] = filename  # Map original URL to local filename
            
            print(f"Downloaded: {filename}")
            
        except requests.RequestException as e:
            print(f"Failed to download {url}: {e}")

    def extract_and_save_tables(self, soup, url):
        """Extract all visible tables, update image references, and save as HTML"""
        try:
            # Find all visible tables
            tables = [table for table in soup.find_all('table') if self.is_element_visible(table)]
            
            if tables:
                # Download images within tables
                for table in tables:
                    for img in table.find_all('img'):
                        src = img.get('src')
                        if src:
                            full_url = urljoin(url, src)
                            if self.is_media_file(full_url) and full_url.lower().endswith(self.image_types):
                                filename = os.path.basename(urlparse(full_url).path) or f"table_img_{len(self.image_map)}.jpg"
                                self.download_file(full_url, filename, is_image=True)
                                # Update the src to local path (relative to the HTML file)
                                img['src'] = filename
                
                # Create HTML with sorting script and enhanced styling
                html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Extracted Tables</title>
    <style>
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; cursor: pointer; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        tr:nth-child(odd) { background-color: #ffffff; }
        h2 { margin-top: 20px; }
        .sortable th:hover { background-color: #ddd; }
    </style>
    <script>
        function sortTable(n, table) {
            var rows, switching = true, i, x, y, shouldSwitch, dir = "asc", switchcount = 0;
            while (switching) {
                switching = false;
                rows = table.rows;
                for (i = 1; i < (rows.length - 1); i++) {
                    shouldSwitch = false;
                    x = rows[i].getElementsByTagName("TD")[n];
                    y = rows[i + 1].getElementsByTagName("TD")[n];
                    var xContent = x.textContent.toLowerCase();
                    var yContent = y.textContent.toLowerCase();
                    if (dir == "asc") {
                        if (xContent > yContent) {
                            shouldSwitch = true;
                            break;
                        }
                    } else if (dir == "desc") {
                        if (xContent < yContent) {
                            shouldSwitch = true;
                            break;
                        }
                    }
                }
                if (shouldSwitch) {
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchcount++;
                } else if (switchcount == 0 && dir == "asc") {
                    dir = "desc";
                    switching = true;
                }
            }
        }
        document.addEventListener("DOMContentLoaded", function() {
            var tables = document.getElementsByClassName("sortable");
            for (var t = 0; t < tables.length; t++) {
                var headers = tables[t].getElementsByTagName("th");
                for (var i = 0; i < headers.length; i++) {
                    headers[i].addEventListener("click", (function(tableIndex, colIndex) {
                        return function() { sortTable(colIndex, tables[tableIndex]); };
                    })(t, i));
                }
            }
        });
    </script>
</head>
<body>
    
"""
                # Add each table with a heading
                for i, table in enumerate(tables, 1):
                    # Preserve or add the sortable class
                    if 'sortable' not in table.get('class', []):
                        table['class'] = table.get('class', []) + ['sortable']
                    else:
                        table['class'] = table.get('class', [])
                    
                    preceding_h = table.find_previous(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    table_title = f"Table {i}" if not preceding_h else f"Table {i}: {preceding_h.get_text(strip=True)}"
                    html_content += f"    <h2>{table_title}</h2>\n    {str(table)}\n"
                
                html_content += """</body>
</html>"""
                
                # Save to file
                table_file = self.download_dir / "extracted_tables.html"
                with open(table_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"Saved {len(tables)} table(s) to: {table_file}")
            else:
                print("No visible tables found on the page")
        except Exception as e:
            print(f"Failed to extract or save tables: {e}")

    def scrape_page(self, url):
        """Scrape a single page for visible media, PDFs, and tables"""
        if self.is_cancelled or url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract and save all visible tables (including image handling)
            self.extract_and_save_tables(soup, url)
            
            # Find all visible images (outside tables)
            for img in soup.find_all('img'):
                if self.is_cancelled:
                    break
                src = img.get('src')
                if src and self.is_element_visible(img):
                    full_url = urljoin(url, src)
                    if self.is_media_file(full_url) and full_url.lower().endswith(self.image_types):
                        filename = os.path.basename(urlparse(full_url).path) or f"img_{len(self.image_map)}.jpg"
                        self.download_file(full_url, filename, is_image=True)
            
            # Find all visible videos
            for video in soup.find_all('video'):
                if self.is_cancelled:
                    break
                if self.is_element_visible(video):
                    for source in video.find_all('source'):
                        src = source.get('src')
                        if src:
                            full_url = urljoin(url, src)
                            if self.is_media_file(full_url) and full_url.lower().endswith(self.video_types):
                                filename = os.path.basename(urlparse(full_url).path) or f"vid_{len(os.listdir(self.download_dir))}.mp4"
                                self.download_file(full_url, filename)
            
            # Find all visible PDFs
            for tag in soup.find_all(['embed', 'object', 'a']):
                if self.is_cancelled:
                    break
                if self.is_element_visible(tag):
                    src = tag.get('src') or tag.get('data') or tag.get('href')
                    if src:
                        full_url = urljoin(url, src)
                        if self.is_media_file(full_url) and full_url.endswith('.pdf'):
                            filename = os.path.basename(urlparse(full_url).path) or f"pdf_{len(os.listdir(self.download_dir))}.pdf"
                            self.download_file(full_url, filename)
            
        except requests.RequestException as e:
            print(f"Failed to scrape {url}: {e}")

    def create_image_pdf(self):
        """Create a PDF with downloaded images, skipping those < 300px in width or height"""
        # Legal landscape dimensions
        pdf_width = 355.6  # Width in mm (14 inches)
        pdf_height = 215.9  # Height in mm (8.5 inches)
        
        # Usable area with 5mm borders
        target_width = pdf_width - 10  # 345.6mm
        target_height = pdf_height - 10  # 205.9mm
        
        pdf = FPDF(orientation='L', unit='mm', format='Legal')  # Standard Legal landscape
        pdf.set_auto_page_break(False)
        
        # Set black background
        pdf.set_fill_color(0, 0, 0)  # Black
        
        # Collect all image files
        image_files = [f for f in self.download_dir.iterdir() if f.suffix.lower() in self.image_types]
        
        for image_path in image_files:
            try:
                # Open image and check dimensions
                with Image.open(image_path) as img:
                    img_width, img_height = img.size
                    
                    # Skip images smaller than 300px in width or height
                    if img_width < 300 or img_height < 300:
                        print(f"Skipping {image_path.name} for PDF (size {img_width}x{img_height} < 300px)")
                        continue
                    
                    # Add a new page with black background
                    pdf.add_page()
                    pdf.rect(0, 0, pdf_width, pdf_height, 'F')  # Fill entire page with black
                    
                    # Convert pixel dimensions to mm (assuming 300 DPI)
                    dpi = 300
                    width_mm = img_width * 25.4 / dpi
                    height_mm = img_height * 25.4 / dpi
                    
                    # Calculate scaling to fit Legal page with 5mm borders
                    scale_w = target_width / width_mm
                    scale_h = target_height / height_mm
                    scale = min(scale_w, scale_h)  # Fit within page bounds
                    
                    # Calculate new dimensions
                    new_width = width_mm * scale
                    new_height = height_mm * scale
                    
                    # Center the image within the page
                    x = (pdf_width - new_width) / 2
                    y = (pdf_height - new_height) / 2
                    
                    # Add image to PDF
                    pdf.image(str(image_path), x, y, new_width, new_height)
                    
            except Exception as e:
                print(f"Failed to add {image_path} to PDF: {e}")
        
        # Save the PDF
        pdf_output = self.download_dir / "all_images.pdf"
        pdf.output(pdf_output)
        print(f"Created PDF: {pdf_output}")

    def scrape_website(self, start_url):
        """Main method to scrape and create outputs"""
        print(f"Scraping visible media, PDFs, and tables from: {start_url}")
        print(f"Saving files to: {self.download_dir}")
        
        # Normalize URL
        if not start_url.startswith(('http://', 'https://')):
            start_url = 'https://' + start_url
            
        self.scrape_page(start_url)
        
        # After scraping, create the PDF from images
        if not self.is_cancelled:
            self.create_image_pdf()

    def cancel(self):
        """Cancel the scraping process"""
        self.is_cancelled = True
        print("Cancellation requested...")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scrape visible media, PDFs, and tables from a website, then create outputs')
    parser.add_argument('url', help='Website URL to scrape')
    args = parser.parse_args()
    
    # Create scraper instance
    scraper = WebsiteMediaScraper()
    
    # Start scraping and processing
    try:
        scraper.scrape_website(args.url)
    except KeyboardInterrupt:
        scraper.cancel()
        print("Scraping stopped by user")
    
    print("Process completed!")

if __name__ == "__main__":
    main()
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
        
        # Track visited URLs to avoid duplicates
        self.visited_urls = set()
        
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

    def download_file(self, url, filename):
        """Download a single media file or PDF"""
        try:
            filepath = self.download_dir / filename
            
            # Skip if file already exists
            if filepath.exists():
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
                    
            print(f"Downloaded: {filename}")
            
        except requests.RequestException as e:
            print(f"Failed to download {url}: {e}")

    def scrape_page(self, url):
        """Scrape a single page for visible media and PDFs"""
        if self.is_cancelled or url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all visible images
            for img in soup.find_all('img'):
                if self.is_cancelled:
                    break
                src = img.get('src')
                if src and self.is_element_visible(img):
                    full_url = urljoin(url, src)
                    if self.is_media_file(full_url) and full_url.lower().endswith(self.image_types):
                        filename = os.path.basename(urlparse(full_url).path) or f"img_{len(os.listdir(self.download_dir))}.jpg"
                        self.download_file(full_url, filename)
            
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
        """Create a PDF with all downloaded images using full Legal landscape dimensions"""
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
                # Add a new page with black background
                pdf.add_page()
                pdf.rect(0, 0, pdf_width, pdf_height, 'F')  # Fill entire page with black
                
                # Open image and get dimensions
                with Image.open(image_path) as img:
                    img_width, img_height = img.size
                    
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
        """Main method to scrape and create PDF"""
        print(f"Scraping visible media and PDFs from: {start_url}")
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
    parser = argparse.ArgumentParser(description='Scrape visible media and PDFs from a website, then create an image PDF')
    parser.add_argument('url', help='Website URL to scrape')
    args = parser.parse_args()
    
    # Create scraper instance
    scraper = WebsiteMediaScraper()
    
    # Start scraping and PDF creation
    try:
        scraper.scrape_website(args.url)
    except KeyboardInterrupt:
        scraper.cancel()
        print("Scraping stopped by user")
    
    print("Process completed!")

if __name__ == "__main__":
    main()
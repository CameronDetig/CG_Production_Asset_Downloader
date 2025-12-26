import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

# Configuration
# Go to the blender studio website. 
# Open developer tools (F12)
# Go to the network tab
# refresh the page
# Click on the first request
# Copy the cookie
USER_COOKIE = "cf_clearance=q0n1jLjhBHVbwdQJWGILLgZk78TJK7B4SlRtU_qWph8-1766590461-1.2.1.1-GcPCr4pKB17TlnBNoSD3SZVo0MG2TLLVYV0Z9KdNvfSvOD12Sq6_h.G74YJSXlkxRvuzMw1zst30R7HZAqXcq.gGv9hX_AyY4L6Fl1o01pU9fHuGF2bEipuq.VgZBz7s5zI2pEUrwUA89oSjb.Ie7wa9qDdA7QMLLS31kdFJptZZlDdUOECE6zompH1xvl2_jiEnWIRKKeJjfhGrFE7pvejtwvvDXCcpMUv93grNPnY; bstudiocsrftoken=B1RVdFnMbb1s2dFtwZUag54rof11Dxfq; sessionid=beczp39ucldbst8ae8onwtm5rb8l2kzd"

BASE_URL = "https://studio.blender.org"
# User requested URL
GALLERY_URL = "https://studio.blender.org/projects/charge/3a6732058f6cb4/"
DOWNLOAD_DIR = "data/charge/asset_development"

def get_soup(url, session):
    try:
        response = session.get(url)
        if response.status_code != 200:
            print(f"Error fetching {url}: Status {response.status_code}")
            return None
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Exception fetching {url}: {e}")
        return None

def download_file(url, session, output_dir, filename=None):
    if not filename:
        filename = url.split('/')[-1]
        if '?' in filename:
            filename = filename.split('?')[0]
        
    path = os.path.join(output_dir, filename)
    
    if os.path.exists(path):
        print(f"  [Skipping] {filename} already exists.")
        return

    print(f"  [Downloading] {filename}...")
    try:
        with session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"  [Done] Saved to {path}")
    except Exception as e:
        print(f"  [Error] Failed to download {url}: {e}")

def visit_gallery(url, session, current_path, visited):
    if url in visited:
        print(f"  [Skipping] Already visited {url}")
        return
    visited.add(url)
    
    print(f"\n[Gallery] Visiting: {url}")
    soup = get_soup(url, session)
    if not soup:
        return
        
    if not os.path.exists(current_path):
        os.makedirs(current_path)

    # 1. Process Files
    asset_links = soup.find_all('a', class_='file-modal-link')
    if asset_links:
        print(f"  Found {len(asset_links)} files in {os.path.basename(current_path) or 'root'}.")
        for i, link in enumerate(asset_links):
            api_url = link.get('data-url')
            if not api_url:
                continue
            
            # print(f"  Processing file {i+1}/{len(asset_links)}...")
            full_api_url = urljoin(BASE_URL, api_url)
            asset_soup = get_soup(full_api_url, session)
            if not asset_soup:
                continue

            download_btn = asset_soup.select_one('a.btn-primary.btn-link')
            
            if download_btn and 'href' in download_btn.attrs:
                download_url = urljoin(BASE_URL, download_btn['href'])
                
                if 'download' in download_btn.attrs:
                    filename = download_btn['download']
                else:
                    filename = download_url.split('/')[-1]
                    if '?' in filename:
                        filename = filename.split('?')[0]
                
                download_file(download_url, session, current_path, filename)

    # 2. Process Sub-Folders
    cards = soup.find_all(class_='cards-item')
    print(f"  Found {len(cards)} cards (potential folders).")
    
    for card in cards:
        link = card.find('a')
        if not link:
            continue
            
        href = link.get('href')
        if not href:
            continue
            
        full_folder_url = urljoin(BASE_URL, href)
        
        # Check if it looks like a project gallery link
        # Recursion logic: if it starts with /projects/spring/ and not 'gallery' (if avoiding main gallery)
        # But wait, original request was a sub-page.
        if '/projects/charge/' in full_folder_url and 'download-source' not in full_folder_url:
             # Try to get a folder name
             title_el = card.find(class_='cards-item-title')
             folder_name = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)
             
             clean_name = "".join([c for c in folder_name if c.isalnum() or c in (' ', '-', '_')]).strip()
             if not clean_name:
                 clean_name = "folder_" + href.split('/')[-2]
             
             # Avoid re-visiting parent or self (handled by visited set but good to check)
             print(f"    Found folder: {clean_name} -> {href}")
             new_path = os.path.join(current_path, clean_name)
             visit_gallery(full_folder_url, session, new_path, visited)

def main():
    print("Starting script...")
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Cookie': USER_COOKIE
    })

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    visited = set()
    visit_gallery(GALLERY_URL, session, DOWNLOAD_DIR, visited)
    print("Script finished.")

if __name__ == "__main__":
    main()

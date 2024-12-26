import requests
import os
import time
from urllib.parse import quote_plus
from tqdm import tqdm
import re
import xml.etree.ElementTree as ET

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_filtered_image_urls(queryURL, exclude_tags, user_limit):
    page_id = 0
    filtered_posts = []
    total_downloaded = 0

    while True:
        try:
            url = f"{queryURL}&pid={page_id}"
            postResponse = requests.get(url, headers=headers)
            postResponse.raise_for_status()
            root = ET.fromstring(postResponse.content)
            posts = root.findall('post')
            
            if not posts:
                break

            for post in posts:
                tags = post.get('tags', '').split()
                # Vérifier si aucun tag exclu n'est présent
                if not any(tag in tags for tag in exclude_tags):
                    file_url = post.get('file_url')
                    if file_url:
                        filtered_posts.append(post)
                        total_downloaded += 1

                if user_limit and total_downloaded >= user_limit:
                    return filtered_posts

            page_id += 1

        except Exception as e:
            print(f'Error: {e}')
            break

    return filtered_posts

def download_file(url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement de {url}: {e}")
        return None

def save_file(file_content, url, folder_name):
   filename = url.split('/')[-1].split('?')[0]
   filepath = os.path.join(folder_name, filename)
   if os.path.exists(filepath):
       existing_file_content = open(filepath, 'rb').read()
       if existing_file_content == file_content:
           return 
       else:
           os.remove(filepath)
   try:
       with open(filepath, 'wb') as f:
           f.write(file_content)
       return f"Fichier enregistré sous {filepath}"
   except Exception as e:
       return f"Erreur lors de la sauvegarde du fichier {filename}: {e}"

def process_files(posts, search_tags):
    folder_name = '_'.join(search_tags.split())
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    total_files = len(posts)
    
    try:
        with tqdm(total=total_files, desc="Téléchargement des fichiers", unit="file", ncols=100) as pbar:
            for post in posts:
                file_url = post.get('file_url')
                if file_url:
                    file_content = download_file(file_url)
                    if file_content:
                        save_file(file_content, file_url, folder_name)
                pbar.update(1)
                time.sleep(0.10)
    finally:
        pbar.close()

def main():
    search_tags = input("Entrez les tags pour la recherche (séparés par des espaces) : ").strip()
    exclude_tags = input("Entrez les tags à exclure (séparés par des espaces) : ").strip()
    user_limit = input("Entrez la limite de téléchargement des fichiers : ").strip()

    encoded_tags = quote_plus(search_tags)
    queryURL = f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&tags={encoded_tags}&limit=100"
    
    user_limit = int(user_limit) if user_limit.isdigit() else None
    exclude_tags = exclude_tags.split() if exclude_tags else []

    posts = fetch_filtered_image_urls(queryURL, exclude_tags, user_limit)
    if posts:
        print(f"Total des fichiers trouvés: {len(posts)}")
        process_files(posts, search_tags)  # Ajout du paramètre search_tags
    else:
        print("Aucun fichier trouvé.")

if __name__ == "__main__":
    try:
        main()
    finally:
        time.sleep(1)
        # Remplacement de os.sync() par un flush des buffers
        try:
            import sys
            sys.stdout.flush()
            sys.stderr.flush()
        except:
            pass

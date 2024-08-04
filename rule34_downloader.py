from rule34Py import rule34Py
import requests
from PIL import Image
from io import BytesIO
import os
import time
from tqdm import tqdm

# Créez une instance de Rule34
rule34 = rule34Py()

def fetch_filtered_image_urls(tags, exclude_tags, user_limit):
    tags_list = tags.split()
    page_id = 1
    filtered_posts = []
    total_downloaded = 0

    while True:
        posts = rule34.search(tags=tags_list, page_id=page_id)
        if not posts:
            break
        for post in posts:
            if not any(exclude_tag in post.tags for exclude_tag in exclude_tags):
                filtered_posts.append(post)
                total_downloaded += 1
                if user_limit and total_downloaded >= user_limit:
                    return filtered_posts
        page_id += 1

    return filtered_posts

def download_file(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement de {url}: {e}")
        return None

def save_file(file_content, url):
    filename = url.split('/')[-1].split('?')[0]
    filepath = os.path.join('downloads', filename)
    if os.path.exists(filepath):
        existing_file_content = open(filepath, 'rb').read()
        if existing_file_content == file_content:
            return f"Le fichier {filename} est déjà présent, téléchargement ignoré."
        else:
            os.remove(filepath)
    try:
        with open(filepath, 'wb') as f:
            f.write(file_content)
        return f"Fichier enregistré sous {filepath}"
    except Exception as e:
        return f"Erreur lors de la sauvegarde du fichier {filename}: {e}"

def process_files(posts):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    total_files = len(posts)
    
    with tqdm(total=total_files, desc="Téléchargement des fichiers", unit="file", ncols=100, position=0, leave=True) as pbar:
        for post in posts:
            if post.content_type == "image":
                file_content = download_file(post.image)
                if file_content:
                    save_file(file_content, post.image)
            elif post.content_type == "video":
                file_content = download_file(post.video)
                if file_content:
                    save_file(file_content, post.video)

            pbar.update(1)
            time.sleep(0.10)  # Délai entre les requêtes

def main():
    search_tags = input("Entrez les tags pour la recherche (séparés par des espaces) : ")
    exclude_tags = input("Entrez les tags à exclure (séparés par des espaces) : ").split()
    user_limit = input("Entrez la limite de téléchargement des fichiers (laissez vide pour aucune limite) : ")

    if user_limit.strip() == "":
        user_limit = None
    else:
        try:
            user_limit = int(user_limit)
        except ValueError:
            print("La limite doit être un nombre entier. Aucune limite ne sera appliquée.")
            user_limit = None

    posts = fetch_filtered_image_urls(search_tags, exclude_tags, user_limit)
    if posts:
        print(f"Total des fichiers trouvés: {len(posts)}")
        process_files(posts)
    else:
        print("Aucun fichier trouvé.")

if __name__ == "__main__":
    main()

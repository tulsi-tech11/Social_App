import os, glob
template_dir = 'd:/25september/Django/velora_env_ready/velora_env/velora_env/velora/myapp/templates/myapp/'
html_files = glob.glob(os.path.join(template_dir, '*.html'))
for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
    new_content = content.replace('<i class="fa-solid fa-film"></i></span><span class="nav-label">Create Reel', '<i class="fa-regular fa-square-caret-right"></i></span><span class="nav-label">Create Reel')
    new_content = new_content.replace('<i class="fa-solid fa-film"></i> Create Reel', '<i class="fa-regular fa-square-caret-right"></i> Create Reel')
    new_content = new_content.replace('<i class="fa-solid fa-clapperboard"></i> Create Reel', '<i class="fa-regular fa-square-caret-right"></i> Create Reel')
    if content != new_content:
        with open(file_path, 'w', encoding='utf-8') as f: f.write(new_content)
        print(f'Updated {file_path}')

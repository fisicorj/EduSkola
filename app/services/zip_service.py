import os
import zipfile
from flask import send_file

def criar_zip_modelos(pasta_modelos='modelos', nome_zip='modelos.zip'):
    zip_path = os.path.join(pasta_modelos, nome_zip)
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(pasta_modelos):
            for file in files:
                if file.endswith('.xlsx'):
                    zipf.write(os.path.join(root, file),
                               arcname=file)
    return zip_path


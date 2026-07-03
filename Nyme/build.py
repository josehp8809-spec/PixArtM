"""
build.py — Script de compilación para Render.
Descarga Node.js de forma portátil, configura el PATH y compila la app Reflex.
"""
import os
import sys
import urllib.request
import tarfile
import subprocess

def install_node():
    node_dir = os.path.join(os.getcwd(), "node_bin")
    if os.path.exists(node_dir) and os.path.exists(os.path.join(node_dir, "bin", "node")):
        print("[Build] Node.js ya está instalado.")
        return node_dir
    
    os.makedirs(node_dir, exist_ok=True)
    # Descargar Node.js portátil para Linux x64 (Render corre sobre Ubuntu)
    url = "https://nodejs.org/dist/v18.17.0/node-v18.17.0-linux-x64.tar.xz"
    archive_path = os.path.join(node_dir, "node.tar.xz")
    print(f"[Build] Descargando Node.js desde {url}...")
    
    # Descargar con cabecera de User-Agent para evitar bloqueos
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req) as response, open(archive_path, 'wb') as out_file:
        out_file.write(response.read())
    
    print("[Build] Extrayendo Node.js...")
    with tarfile.open(archive_path, "r:xz") as tar:
        tar.extractall(path=node_dir)
    
    extracted_folder = os.path.join(node_dir, "node-v18.17.0-linux-x64")
    # Mover archivos de la carpeta extraída a node_dir
    for item in os.listdir(extracted_folder):
        src = os.path.join(extracted_folder, item)
        dst = os.path.join(node_dir, item)
        if os.path.exists(dst):
            if os.path.isdir(dst):
                import shutil
                shutil.rmtree(dst)
            else:
                os.remove(dst)
        os.rename(src, dst)
    os.rmdir(extracted_folder)
    os.remove(archive_path)
    print("[Build] Node.js instalado correctamente en node_bin/")
    return node_dir

def main():
    node_dir = install_node()
    node_bin_dir = os.path.join(node_dir, "bin")
    
    # Agregar Node al PATH temporal
    os.environ["PATH"] = node_bin_dir + os.pathsep + os.environ.get("PATH", "")
    print("[Build] PATH configurado:", os.environ["PATH"])
    
    # Validar instalación
    try:
        node_version = subprocess.check_output(["node", "--version"]).decode().strip()
        print(f"[Build] Versión de Node.js validada: {node_version}")
        npm_version = subprocess.check_output(["npm", "--version"]).decode().strip()
        print(f"[Build] Versión de NPM validada: {npm_version}")
    except Exception as e:
        print("[Build] ❌ Error validando Node/NPM:", e)
        sys.exit(1)
        
    # Instalar dependencias de python
    print("[Build] Instalando dependencias de requirements.txt...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Iniciar Reflex y exportar
    print("[Build] Inicializando Reflex...")
    subprocess.check_call(["reflex", "init"])
    
    print("[Build] Exportando frontend de Reflex...")
    subprocess.check_call(["reflex", "export", "--frontend-only", "--no-zip"])
    print("[Build] ✅ ¡Compilación completada con éxito!")

if __name__ == "__main__":
    main()

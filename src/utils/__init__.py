"""
Utilidades generales para el proyecto DocN8NAgent
"""
import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json


def generate_file_hash(file_path: str, algorithm: str = 'md5') -> str:
    """Genera hash de un archivo"""
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Obtiene información detallada de un archivo"""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
    
    stat = path.stat()
    mime_type, _ = mimetypes.guess_type(str(path))
    
    return {
        'name': path.name,
        'size': stat.st_size,
        'extension': path.suffix.lower(),
        'mime_type': mime_type or 'application/octet-stream',
        'created': datetime.fromtimestamp(stat.st_ctime),
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'hash': generate_file_hash(file_path)
    }


def validate_file_type(file_path: str, allowed_types: list) -> bool:
    """Valida si un archivo es de un tipo permitido"""
    extension = Path(file_path).suffix.lower()
    return extension in allowed_types


def safe_filename(filename: str) -> str:
    """Sanitiza un nombre de archivo para uso seguro"""
    # Eliminar caracteres peligrosos
    unsafe_chars = '<>:"/\\|?*'
    safe_name = ''.join(c for c in filename if c not in unsafe_chars)
    
    # Limitar longitud
    if len(safe_name) > 255:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:250] + ext
    
    return safe_name


def format_file_size(size_bytes: int) -> str:
    """Formatea el tamaño de archivo en formato legible"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def create_backup_filename(original_path: str) -> str:
    """Crea un nombre de archivo de respaldo único"""
    path = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return str(path.parent / f"{path.stem}_{timestamp}{path.suffix}")


def ensure_directory(directory: str) -> Path:
    """Asegura que un directorio exista, creándolo si es necesario"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json_config(config_path: str) -> Dict[str, Any]:
    """Carga configuración desde archivo JSON"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Error en archivo JSON {config_path}: {e}")


def save_json_config(config: Dict[str, Any], config_path: str) -> None:
    """Guarda configuración en archivo JSON"""
    ensure_directory(Path(config_path).parent)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False, default=str)

import importlib.util
import os


def load_config(config_path: str, config_key: str = "CONFIG"):
    """
    Carga un diccionario de configuración desde un archivo Python.

    Args:
        config_path: ruta al archivo de configuración (.py)
        config_key: nombre de la variable de configuración en el archivo (ej: "DB_CONFIG", "MONGO_CONFIG")

    Returns:
        dict: El diccionario de configuración

    Raises:
        FileNotFoundError: Si el archivo no existe
        AttributeError: Si la clave de configuración no existe en el archivo
    """
    path = os.path.abspath(config_path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {path}")

    spec = importlib.util.spec_from_file_location("config_module", path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    if not hasattr(config_module, config_key):
        raise AttributeError(f"El archivo {path} debe contener un diccionario {config_key}")

    return getattr(config_module, config_key)

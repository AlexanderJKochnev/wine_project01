# streamlit_app/config/utils.py
from pathlib import Path
def get_path_to_root(name: str = '.env'):
    """
        get path to file or directory in root directory
    """
    for k in range(1, 10):
        env_path = Path(__file__).resolve().parents[k] / name
        if env_path.exists():
            break
    else:
        env_path = None
        raise Exception('environment file is not found')
    return env_path
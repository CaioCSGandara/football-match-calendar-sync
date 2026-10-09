from pathlib import Path
import random
from typing import Dict, List
from app.utils.yaml_reader import read_yaml

CONFIG_FILE_PATH = Path(__file__).parent / "config" / "browser_profiles.yaml"
BROWSER_PROFILES: List[Dict[str, str]] = read_yaml(CONFIG_FILE_PATH).get("browser_profiles", [])


def get_random_browser_profile() -> Dict[str, str]:
    """Seleciona aleatoriamente um par de perfil (client_identifier e user_agent)."""
    return random.choice(BROWSER_PROFILES)

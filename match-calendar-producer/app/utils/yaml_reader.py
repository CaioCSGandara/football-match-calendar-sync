from pathlib import Path
from typing import Any, Union
import yaml


def read_yaml(file_path: Union[str, Path]) -> Any:
    """
    Lê um arquivo YAML no caminho especificado e retorna seu conteúdo estruturado.

    :param file_path: Caminho para o arquivo YAML (str ou Path).
    :return: Conteúdo parsed do arquivo YAML.
    :raises FileNotFoundError: Se o arquivo não for encontrado.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo YAML não encontrado: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

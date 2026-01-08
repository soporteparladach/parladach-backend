import logging
import sys


def configure_logging(app_env: str) -> None:
    """
    Logging básico en consola.
    - Formato consistente
    - Nivel según entorno
    """
    level = logging.DEBUG if app_env in {"local", "dev", "development"} else logging.INFO

    logging.basicConfig(
        level=level,
        stream=sys.stdout,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    # Reduce ruido de librerías comunes
    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)

import logging
import os


def setup_logger(name, log_dir="logs"):
    """Set up a logger with a file handler specific to the module name."""
    # Ensure the log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Create a logger using the module's name
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set the default logging level

    # Avoid adding handlers multiple times
    if not logger.handlers:
        # Create a file handler with a module-specific log file
        log_file = os.path.join(log_dir, f"{name.replace('.', '_')}.log")
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.DEBUG)

        # Create a formatter and attach it to the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)

        # Prevent propagation to ancestor loggers (e.g., root logger)
        logger.propagate = False

    return logger

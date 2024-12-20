"""Logging configuration for the application."""
import os
import sys
import logfire

def setup_logging():
    """Configure logging for the application."""
    # Configure logfire with minimal settings
    logfire.configure()

    # Set log level based on environment variable
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Add any additional configuration if needed
    logfire.info(f"Logging initialized with level: {log_level}")

    # Configure error handling
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Call the default handler for keyboard interrupt
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logfire.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    # Set the exception handler
    sys.excepthook = handle_exception
import json
import os
import logging


class SystemConfig:
    def __init__(self):
        self.config = {
            "printer": ""
        }
        self.config_file = "system_config.json"
        self.load_config()

    def load_config(self):
        """Load system configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                logging.info("System configuration loaded successfully")
            else:
                logging.warning("System configuration file not found, using default configuration")
                # Create default config file
                self.save_config(self.config)
        except Exception as e:
            logging.error(f"Error loading system configuration: {str(e)}")
            self.config = {"printer": ""}

    def save_config(self, config_data):
        """Save system configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f)
            self.config = config_data
            logging.info("System configuration saved successfully")
            return True
        except Exception as e:
            logging.error(f"Error saving system configuration: {str(e)}")
            return False

    def get_printer(self):
        """Get the default printer name."""
        return self.config.get("printer", "")

    def get_config(self):
        """Get the entire configuration dictionary."""
        return self.config.copy()  # Return a copy to prevent external modification

# Create global instances
system_config = SystemConfig()


def load_system_config():
    system_config.load_config()

def save_system_config(config_data):
    return system_config.save_config(config_data)

def get_default_printer():
    return system_config.get_printer() 
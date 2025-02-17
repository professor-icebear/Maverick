import os
from pathlib import Path
import logging
import subprocess
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / 'maverick_data'
        self.dataset_dir = self.data_dir / 'phh-dataset'
        
    def setup(self) -> bool:
        """Set up the data directory and download the dataset."""
        try:
            # Create data directories
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Clone the dataset if it doesn't exist
            if not self.dataset_dir.exists():
                logger.info("Downloading PHH dataset...")
                result = subprocess.run(
                    ['git', 'clone', 'https://github.com/uoftcprg/phh-dataset.git'],
                    cwd=self.data_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.error(f"Failed to clone dataset: {result.stderr}")
                    return False
                
                logger.info("Dataset downloaded successfully")
            else:
                logger.info("Dataset already exists")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up data: {e}")
            return False
    
    def get_data_paths(self) -> list[Path]:
        """Get paths to all .phh files in the dataset."""
        if not self.dataset_dir.exists():
            logger.error("Dataset directory not found. Run setup() first.")
            return []
        
        return list(self.dataset_dir.glob('**/*.phh'))
    
    def update_dataset(self) -> bool:
        """Pull latest changes from the dataset repository."""
        try:
            if not self.dataset_dir.exists():
                logger.error("Dataset directory not found. Run setup() first.")
                return False
            
            logger.info("Updating dataset...")
            result = subprocess.run(
                ['git', 'pull'],
                cwd=self.dataset_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to update dataset: {result.stderr}")
                return False
            
            logger.info("Dataset updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating dataset: {e}")
            return False 
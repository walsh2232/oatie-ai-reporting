"""Test configuration for pytest."""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Test environment configuration
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///test.db"
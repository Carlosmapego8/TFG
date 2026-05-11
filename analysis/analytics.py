"""
Analytics component for the orchestrator pipeline.
Generates and validates the Power BI PBIP project based on gold layer views.
"""

import os
import sys
from pathlib import Path
import traceback

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "ingestion"))

from config_loader import load_config
from .pbip_generator import generate_pbip_project


class Analytics:
    """
    Analytics component that generates Power BI PBIP project.
    Called by Orchestrator after transformations are complete.
    """

    def __init__(self, db_config_path: str, output_dir: str = None):
        """
        Initialize Analytics component.

        Args:
            db_config_path: Path to the Python file with DB_CONFIG dictionary
            output_dir: Directory where PBIP files will be created (default: current dir)
        """
        self.db_config_path = db_config_path
        self.output_dir = output_dir or os.getcwd()
        self.db_config = None

    def _load_db_config(self):
        """Load database configuration from Python file"""
        try:
            self.db_config = load_config(self.db_config_path, "DB_CONFIG")
            print(f"✅ Database config loaded from {self.db_config_path}")
            return True
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            return False
        except AttributeError as e:
            print(f"❌ Error: {e}")
            return False

    def _validate_gold_schema(self):
        """
        Validate that gold schema exists and tables are accessible.
        (Optional: can be enhanced to actually test the connection)
        """
        print("ℹ️  Gold schema validation: Skipped (connection test in Power BI Desktop)")
        # In a more complete implementation, could use psycopg2 to test connection
        return True

    def run(self):
        """
        Main entry point called by Orchestrator.
        Generates the PBIP project for Power BI.
        """
        print("\n" + "=" * 70)
        print("📊 ANALYTICS: Generating Power BI PBIP Project")
        print("=" * 70 + "\n")

        try:
            # Step 1: Load database configuration
            print("Step 1/3: Loading database configuration...")
            if not self._load_db_config():
                return False

            # Step 2: Validate gold schema accessibility
            print("\nStep 2/3: Validating gold schema...")
            if not self._validate_gold_schema():
                return False

            # Step 3: Generate PBIP project
            print("\nStep 3/3: Generating PBIP project...")
            project_path = generate_pbip_project(self.db_config, self.output_dir)

            print("\n" + "=" * 70)
            print("✅ PBIP PROJECT GENERATED SUCCESSFULLY")
            print("=" * 70)
            print(f"\n📍 Location: {project_path}")
            print("\n📖 Next steps:")
            print("   1. Ensure PostgreSQL ODBC driver is installed on your machine")
            print("   2. Open Power BI Desktop")
            print("   3. Enable PBIP support: File → Options → Preview Features → Power BI Projects")
            print(f"   4. Open the project file: {Path(project_path) / 'euro_analysis.pbip'}")
            print("   5. Configure/refresh the PostgreSQL connection with your credentials")
            print("   6. Create visualizations using the tables, relationships, and measures\n")

            return True

        except Exception as e:
            print(f"\n❌ ERROR in Analytics.run(): {e}")
            traceback.print_exc()
            return False


if __name__ == "__main__":
    # Example usage
    analytics = Analytics(db_config_path="db_config.py", output_dir=".")
    success = analytics.run()
    sys.exit(0 if success else 1)

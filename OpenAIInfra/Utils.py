import os


def load_env_file():
    """Load .env file with better error handling and debugging."""
    try:
        from dotenv import load_dotenv

        # Try loading from current directory first
        current_dir = os.getcwd()
        env_path = os.path.join(current_dir, '.env')

        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"✅ Loaded .env from: {env_path}")
            return True
        else:
            # Try loading from script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            env_path = os.path.join(script_dir, '.env')

            if os.path.exists(env_path):
                load_dotenv(env_path)
                print(f"✅ Loaded .env from: {env_path}")
                return True
            else:
                print(f"⚠️  No .env file found in {current_dir} or {script_dir}")
                return False

    except ImportError:
        print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
        return False

    except Exception as e:
        print(f"⚠️  Error loading .env file: {e}")
        return False
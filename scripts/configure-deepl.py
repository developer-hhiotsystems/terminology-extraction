#!/usr/bin/env python
"""Configure DeepL API key"""
import sys
from pathlib import Path

def main():
    print("\n" + "="*50)
    print("  DeepL API Configuration")
    print("="*50 + "\n")

    env_path = Path(".env")

    if not env_path.exists():
        print("[ERROR] .env file not found")
        print("Please run this script from the project root directory\n")
        sys.exit(1)

    # Check current configuration
    content = env_path.read_text()

    if "YOUR_DEEPL_API_KEY_HERE" not in content:
        print("[INFO] DeepL API key appears to be already configured")
        print("\nCurrent .env content (DEEPL_API_KEY line):")
        for line in content.split('\n'):
            if 'DEEPL_API_KEY' in line and not line.strip().startswith('#'):
                print(f"  {line}")

        reconfigure = input("\nReconfigure API key? (y/n): ").lower()
        if reconfigure != 'y':
            print("\nCancelled.\n")
            sys.exit(0)

    # Guide user to get API key
    print("\nDeepL API Key Setup:")
    print("-" * 50)
    print("1. Visit: https://www.deepl.com/pro-api")
    print("2. Sign up for DeepL API Free tier")
    print("   - Free: 500,000 characters/month")
    print("   - No credit card required")
    print("3. Verify your email address")
    print("4. Go to Account Settings")
    print("5. Find 'API Keys' section")
    print("6. Copy your API key")
    print("")

    open_browser = input("Open DeepL API signup page in browser? (y/n): ").lower()
    if open_browser == 'y':
        import webbrowser
        webbrowser.open("https://www.deepl.com/pro-api")
        print("\nBrowser opened. Complete signup and return here.")

    print("\n" + "-"*50)
    api_key = input("Enter your DeepL API key (or 'skip' to skip): ").strip()

    if api_key.lower() == 'skip':
        print("\n[INFO] Skipping configuration. You can run this script again later.\n")
        sys.exit(0)

    if not api_key or len(api_key) < 10:
        print("\n[ERROR] Invalid API key. Key should be longer than 10 characters.\n")
        sys.exit(1)

    # Update .env file
    new_content = content.replace("YOUR_DEEPL_API_KEY_HERE", api_key)

    if new_content == content:
        # Key was already configured, replace it
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'DEEPL_API_KEY=' in line and not line.strip().startswith('#'):
                lines[i] = f"DEEPL_API_KEY={api_key}"
                break
        new_content = '\n'.join(lines)

    env_path.write_text(new_content)
    print("\n[OK] DeepL API key configured successfully!")

    # Test the API key
    print("\nTesting API key...")
    try:
        import deepl
        translator = deepl.Translator(api_key)

        # Test with a small translation
        result = translator.translate_text("Hello", target_lang="DE")
        print(f"[OK] API key is valid! Test translation: 'Hello' -> '{result.text}'")

        # Get usage statistics
        usage = translator.get_usage()
        if usage.character.limit_exceeded:
            print(f"[WARN] Character limit exceeded: {usage.character.count}/{usage.character.limit}")
        else:
            remaining = usage.character.limit - usage.character.count
            print(f"[INFO] Remaining characters: {remaining:,} / {usage.character.limit:,}")

        print("\n[OK] DeepL API is ready to use!\n")

    except deepl.exceptions.AuthorizationException:
        print("[ERROR] Invalid API key. Please check your key and try again.\n")
        sys.exit(1)
    except Exception as e:
        print(f"[WARN] Could not test API key: {e}")
        print("API key saved, but verification failed.")
        print("Make sure you have internet connection.\n")

if __name__ == "__main__":
    main()

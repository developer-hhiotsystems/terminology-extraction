#!/usr/bin/env python
"""Download and setup IATE terminology database"""
import sys
import webbrowser
from pathlib import Path

def main():
    print("\n" + "="*50)
    print("  IATE Dataset Download Helper")
    print("="*50 + "\n")

    iate_dir = Path("data/iate")
    iate_dir.mkdir(parents=True, exist_ok=True)

    # Check if dataset already exists
    tbx_files = list(iate_dir.glob("*.tbx"))
    csv_files = list(iate_dir.glob("*.csv"))

    if tbx_files or csv_files:
        print("[INFO] IATE dataset files found:")
        for file in tbx_files + csv_files:
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  - {file.name} ({size_mb:.1f} MB)")

        redownload = input("\nDownload new dataset? (y/n): ").lower()
        if redownload != 'y':
            print("\nUsing existing dataset.\n")
            sys.exit(0)

    # Guide user to download
    print("\nIATE (Inter-Active Terminology for Europe) Dataset:")
    print("-" * 50)
    print("IATE is the EU's terminology database containing:")
    print("  - 8+ million terms")
    print("  - 24 EU languages")
    print("  - Technical and legal terminology")
    print("")
    print("Download Information:")
    print("  - URL: https://iate.europa.eu/download-iate")
    print("  - Format: TBX (TermBase eXchange) or CSV")
    print("  - Size: ~500 MB compressed")
    print("  - Download time: 5-10 minutes")
    print("  - No account required")
    print("")

    open_browser = input("Open IATE download page in browser? (y/n): ").lower()
    if open_browser == 'y':
        webbrowser.open("https://iate.europa.eu/download-iate")
        print("\nBrowser opened. Follow these steps:")
    else:
        print("\nManual download steps:")

    print("\n" + "-"*50)
    print("Download Steps:")
    print("1. Visit: https://iate.europa.eu/download-iate")
    print("2. Choose format:")
    print("   - TBX format (Recommended for XML parsing)")
    print("   - CSV format (Easier to process)")
    print("3. Click Download")
    print("4. Wait for download to complete (~5-10 minutes)")
    print("5. Save file to:")
    print(f"   {iate_dir.absolute()}")
    print("")

    print("Recommended filename: IATE_export.tbx (or .csv)")
    print("-"*50 + "\n")

    input("Press Enter when download is complete...")

    # Check if file was downloaded
    tbx_files = list(iate_dir.glob("*.tbx"))
    csv_files = list(iate_dir.glob("*.csv"))

    if tbx_files or csv_files:
        print("\n[OK] IATE dataset found!")

        all_files = tbx_files + csv_files
        for file in all_files:
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  - {file.name} ({size_mb:.1f} MB)")

        # Check .env configuration
        env_path = Path(".env")
        if env_path.exists():
            content = env_path.read_text()

            # Suggest updating .env if using different filename
            if len(all_files) == 1:
                dataset_file = all_files[0]
                expected_path = f"./data/iate/{dataset_file.name}"

                if "IATE_DATASET_PATH=" in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'IATE_DATASET_PATH=' in line and not line.strip().startswith('#'):
                            current_path = line.split('=')[1].strip()
                            if current_path != expected_path:
                                print(f"\n[INFO] Updating .env with correct path")
                                lines[i] = f"IATE_DATASET_PATH={expected_path}"
                                env_path.write_text('\n'.join(lines))
                                print(f"[OK] Updated IATE_DATASET_PATH to: {expected_path}")

        print("\n[OK] IATE dataset is ready to use!")
        print("\nNote: IATE releases quarterly updates.")
        print("Set a reminder to download new versions every 3 months.\n")

    else:
        print("\n[WARN] No IATE dataset files found in data/iate/")
        print("\nPlease ensure you:")
        print(f"  1. Downloaded the file from https://iate.europa.eu/download-iate")
        print(f"  2. Saved it to: {iate_dir.absolute()}")
        print("  3. Extracted if it's a compressed archive (.zip, .gz)")
        print("\nRun this script again after downloading.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()

import os
import subprocess
import shutil
import sys
import zipfile

def ask_delete(file_path):
    """Ask user whether to delete a file after operation."""
    choice = input(f"❓ Do you want to delete the original file '{file_path}'? (Y/y for Yes, N/n for No, default is No): ").strip()
    if choice.lower() == "y":
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
            print(f"🗑️ Deleted: {file_path}")
        except Exception as e:
            print(f"⚠️ Could not delete {file_path}: {e}")
    else:
        print(f"✅ Kept original: {file_path}")


def encrypt_folder(folder_path, passphrase):
    if not os.path.isdir(folder_path):
        print(f"❌ Error: Folder '{folder_path}' does not exist.")
        sys.exit(1)

    archive_name = folder_path.rstrip(os.sep) + ".zip"
    shutil.make_archive(folder_path, 'zip', folder_path)

    encrypted_file = archive_name + ".gpg"
    try:
        subprocess.run([
            "gpg",
            "--batch",
            "--yes",
            "--symmetric",
            "--cipher-algo", "AES256",
            "--passphrase", passphrase,
            "-o", encrypted_file,
            archive_name
        ], check=True)
        print(f"✅ Encrypted folder saved as: {encrypted_file}")
    except subprocess.CalledProcessError:
        print("❌ Error: GPG encryption failed.")
        sys.exit(1)

    os.remove(archive_name)
    print(f"🗑️ Deleted temporary archive: {archive_name}")

    # Ask if original folder should be deleted
    ask_delete(folder_path)


def decrypt_folder(encrypted_file, passphrase):
    if not os.path.isfile(encrypted_file):
        print(f"❌ Error: File '{encrypted_file}' does not exist.")
        sys.exit(1)

    decrypted_zip = encrypted_file.replace(".gpg", "")

    try:
        subprocess.run([
            "gpg",
            "--batch",
            "--yes",
            "--decrypt",
            "--passphrase", passphrase,
            "-o", decrypted_zip,
            encrypted_file
        ], check=True)
        print(f"✅ Decrypted file saved as: {decrypted_zip}")
    except subprocess.CalledProcessError:
        print("❌ Error: GPG decryption failed.")
        sys.exit(1)

    # Extract into filename-decrypted
    base_name = os.path.splitext(decrypted_zip)[0]  # remove .zip
    folder_name = f"{base_name}-decrypted"

    with zipfile.ZipFile(decrypted_zip, 'r') as zip_ref:
        zip_ref.extractall(folder_name)
    print(f"📂 Folder extracted to: {folder_name}")

    os.remove(decrypted_zip)
    print(f"🗑️ Deleted temporary decrypted zip: {decrypted_zip}")

    # Ask if original encrypted file should be deleted
    ask_delete(encrypted_file)


def choose_folder():
    current_dir = os.getcwd()
    folders = [f for f in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, f))]

    if not folders:
        print("❌ No folders found in current directory.")
        sys.exit(1)

    print("\n📂 Available folders:")
    for i, folder in enumerate(folders, 1):
        print(f"{i}. {folder}")
    print(f"{len(folders) + 1}. Exit")

    choice = input("Choose a folder: ").strip()

    try:
        choice = int(choice)
        if choice == len(folders) + 1:
            print("👋 Exiting...")
            sys.exit(0)
        elif 1 <= choice <= len(folders):
            return os.path.join(current_dir, folders[choice - 1])
        else:
            print("❌ Invalid choice.")
            sys.exit(1)
    except ValueError:
        print("❌ Invalid input.")
        sys.exit(1)


def choose_gpg_file():
    current_dir = os.getcwd()
    gpg_files = [f for f in os.listdir(current_dir) if f.endswith(".gpg")]

    if not gpg_files:
        print("❌ No .gpg files found in current directory.")
        sys.exit(1)

    print("\n🔑 Available encrypted files:")
    for i, f in enumerate(gpg_files, 1):
        print(f"{i}. {f}")
    print(f"{len(gpg_files) + 1}. Exit")

    choice = input("Choose a file: ").strip()

    try:
        choice = int(choice)
        if choice == len(gpg_files) + 1:
            print("👋 Exiting...")
            sys.exit(0)
        elif 1 <= choice <= len(gpg_files):
            return os.path.join(current_dir, gpg_files[choice - 1])
        else:
            print("❌ Invalid choice.")
            sys.exit(1)
    except ValueError:
        print("❌ Invalid input.")
        sys.exit(1)


def main():
    print("\n=== GPG Folder Encrypt/Decrypt Tool ===")
    print("1. Encrypt a folder")
    print("2. Decrypt a folder")
    print("3. Exit")
    choice = input("Choose an option (1, 2, 3): ").strip()

    if choice == "1":
        folder = choose_folder()
        keyphrase = input("Enter passphrase: ").strip()
        encrypt_folder(folder, keyphrase)
    elif choice == "2":
        enc_file = choose_gpg_file()
        keyphrase = input("Enter passphrase: ").strip()
        decrypt_folder(enc_file, keyphrase)
    elif choice == "3":
        print("👋 Exiting...")
        sys.exit(0)
    else:
        print("❌ Invalid choice. Exiting.")
        sys.exit(1)


if __name__ == "__main__":
    main()

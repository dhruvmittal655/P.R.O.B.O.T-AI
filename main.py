"""Application entry point and basic dependency validation."""

from importlib.util import find_spec


REQUIRED_PACKAGES = {
    "beautifulsoup4": "bs4",
    "customtkinter": "customtkinter",
    "ddgs": "ddgs",
    "ollama": "ollama",
    "Pillow": "PIL",
    "python-docx": "docx",
    "reportlab": "reportlab",
    "requests": "requests",
    "scikit-learn": "sklearn",
    "sentence-transformers": "sentence_transformers",
    "spacy": "spacy",
}

def missing_packages():
    """Return requirement names whose import modules are unavailable."""

    return [
        package
        for package, module in REQUIRED_PACKAGES.items()
        if find_spec(module) is None
    ]


def main():
    missing = missing_packages()

    if missing:
        print("SmartSearch AI cannot start because packages are missing:")
        print(", ".join(missing))
        print("Install them with: pip install -r requirements.txt")
        return

    from gui import SmartSearchGUI

    app = SmartSearchGUI()
    app.run()


if __name__ == "__main__":
    main()

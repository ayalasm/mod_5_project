from setuptools import setup, find_packages

setup(
    name = "salsa-bachata-classifier",
    version = "0.1.0",
    description = "A binary classifier to distinguish between salsa and bachata using Spotify's API",
    author = "Marco Sanchez-Ayala",
    packages = find_packages("src"),
    package_dir = {"": "src"},
    author_email = "sanchezayala.marco@gmail.com",
    install_requires = [
        "numpy==1.22.0",
        "pandas==0.25.3",
        "pytest==5.3.2",
        "spotipy==2.11.2",
    ],
)
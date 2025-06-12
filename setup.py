from setuptools import setup, find_packages

setup(
    name="spotify_organizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "spotipy==2.23.0",
    ],
    python_requires=">=3.6",
) 
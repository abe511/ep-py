from setuptools import setup, find_packages

setup(
    name="rss_reader",
    version="0.1.2",
    description="a simple RSS feed tool",
    packages=find_packages(include=["rss_reader", "rss_reader.*"]),
    install_requires=[
        "beautifulsoup4",
        "lxml",
        "requests"
    ],
    entry_points={
        "console_scripts": ["rss_reader=rss_reader.rss_reader:main"]
    }
)

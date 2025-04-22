from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="web-search-agent",
    author="leepokai",
    author_email="kevin2005ha@gmail.com",
    description="An intelligent web search agent that provides structured results",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leepokai/web-search-agent",
    package_dir={"": "src"},  # select root directory
    packages=find_packages(where="src"),  # return packages where is in src dir
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)

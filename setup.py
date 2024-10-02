from setuptools import setup, find_packages

setup(
    name="pytracetoix",
    version="0.1.0",
    author="Alexandre Bento Freire",
    author_email="devtoix@a-bentofreire.com",
    description="An Input/Result value tracer for debugging purposes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/a-bentofreire/pytracetoix",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
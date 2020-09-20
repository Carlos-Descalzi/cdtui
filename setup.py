import setuptools
import os

with open("README.md", "r") as f:
    long_description = f.read()

requirements=[]
if os.path.isfile('requirements.txt'):
    with open("requirements.txt", "r") as f:
        requirements = f.readlines()

setuptools.setup(
    name="cdtui",
    version="0.0.1",
    author="Carlos Descalzi",
    author_email="carlos.descalzi@gmail.com",
    description="A very rustic component based UI library for terminal applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Carlos-Descalzi/cdtui",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

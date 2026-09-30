"""Package configuration for the Find a Time application."""

from setuptools import find_packages, setup


setup(
    name="find-a-time",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.12",
)

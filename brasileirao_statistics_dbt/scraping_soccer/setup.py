from setuptools import find_packages, setup

setup(
    name="scraping_soccer",
    packages=find_packages(exclude=["scraping_soccer_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagit", "pytest"]},
)

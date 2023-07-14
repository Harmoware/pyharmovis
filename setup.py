from setuptools import setup, find_packages

setup(
    name='pyharmovis',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "jinja2>=2.10.1",
        "numpy>=1.16.4",
    ],
)

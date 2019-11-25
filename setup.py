import io

from setuptools import find_packages
from setuptools import setup

with io.open("README.rst", "rt", encoding="utf8") as f:
    readme = f.read()

setup(
    name="batweb",
    version="1.0.0",
    url="https://github.com/FrancoMaxime/batweb",
    license="MIT",
    maintainer="Maxime Franco",
    maintainer_email="contact@maximefranco.be",
    description="The bat app built in the context of my graduate.",
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask"],
    extras_require={"test": ["pytest", "coverage"]},
)
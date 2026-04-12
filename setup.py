from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in bismillah_ethiobiz/__init__.py
from bismillah_ethiobiz import __version__ as version

setup(
	name="bismillah_ethiobiz",
	version=version,
	description="Beautiful, static branding theme for EthioBiz with glassmorphism design",
	author="Biz Technology Solutions",
	author_email="biz.technology@outlook.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)

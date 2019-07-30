import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = ['pyserial', 'prologix_usb']
# with open('requirements.txt','r') as req:
#      for line in req:
#          requirements.append(line)

from src.scope_control import __version__ as ver

setuptools.setup(
    name="scope_control",
    packages=['scope_control'],
    package_dir={'':'src'},
    version=ver,
    author="Danyal Ahsanullah",
    author_email="danyal.ahsanullah@gmail.com",
    description="interface for controlling gpib scopes via prologix serial interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/an-oreo/PSU_Control",
    # packages=setuptools.find_packages(),
    requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
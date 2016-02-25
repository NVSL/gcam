from setuptools import setup
import os
from codecs import open
import sys

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(os.path.join(here, 'VERSION.txt'), encoding='utf-8') as f:
    version = f.read()


setup(name='gcam',
      version=version,
      description="A tool for rendering Eagle board files and libraries as svgs",
      long_description=long_description,
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Science/Research",
          "Operating System :: MacOS",
          "Operating System :: POSIX",
          "Operating System :: POSIX :: Linux",
          "Operating System :: Unix",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Topic :: Scientific/Engineering",
          "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
          "Topic :: System",
          "Topic :: System :: Hardware",
      ],
      author="NVSL, University of California San Diego",
      author_email="swanson@cs.ucsd.edu",
      url="http://nvsl.ucsd.edu/gcam/",
      test_suite="Test",
      packages = ["GCAM"],
      package_dir={
          'GCAM' : 'GCAM',
      },
      package_data={
          "" : ["*.rst"],
      },
      install_requires=["lxml>=3.4.2",  "Sphinx>=1.3.1", "svgwrite", "Jinja2>=2.7.3"],
      entry_points={
          'console_scripts': [
              'gcam = GCAM.gcam:main',
              'gcam2 = GCAM.gcam2:main',
              'addPackageTo2DModel = GCAM.addPackageTo2DModel:main',
        ]
        },
      keywords = "PCB Eagle CAD printed circuit boards schematic electronics CadSoft",

)



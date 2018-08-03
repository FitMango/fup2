from distutils.core import setup

import fup


VERSION = "0.2.0"


setup(
    name="fup",
    version=VERSION,
    author="Jordan Matelsky",
    author_email="opensource@matelsky.com",
    description=("fup"),
    license="Apache 2.0",
    keywords=[
    ],
    url="https://github.com/FitMango/fup2/tarball/" + VERSION,
    packages=['fup'],
    scripts=[
        'bin/fup'
    ],
    classifiers=[],
    install_requires=[
    ],
)

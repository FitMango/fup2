from distutils.core import setup

import fup

"""
git tag {VERSION}
git push --tags
python setup.py sdist upload -r pypi
"""

VERSION = fup.__version__

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

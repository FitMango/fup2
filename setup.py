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
    license="BSD",
    keywords=[
    ],
    #url="https://github.com/ ... / ... /tarball/" + VERSION,
    packages=['fup'],
    scripts=[
        'bin/fup'
    ],
    classifiers=[],
    install_requires=[
    ],
)

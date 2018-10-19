from distutils.core import setup


VERSION = "0.2.1"


setup(
    name="fup",
    version=VERSION,
    author="Jordan Matelsky",
    author_email="opensource@matelsky.com",
    description=("fup"),
    license="Apache 2.0",
    keywords=[
    ],
    url="https://github.com/FitMango/fup2/",
    packages=['fup'],
    scripts=[
        'bin/fup'
    ],
    classifiers=[],
    install_requires=[
        "boto3",
        "colored",
        "zappa",
        # "pynamodb",
        "click",
    ],
)

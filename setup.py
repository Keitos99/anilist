from setuptools import setup

setup(
    name="anilist",
    version="0.1.2",
    description="A Anilist API",
    url="https://github.com/Agsayan/anilist",
    author="Sayan",
    author_email="",
    license="BSD 2-clause",
    packages=["anilist"],
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
)

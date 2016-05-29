from setuptools import setup, find_packages

import sgsclient


def readme():
    with open("README.rst") as f:
        return f.read()


setup(name="sgsclient",
      version=sgsclient.version,
      description="The python client library for the Stratum Game Server.",
      long_description=readme(),
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Console",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3",
          "Topic :: Games/Entertainment :: Board Games",
          "Topic :: Games/Entertainment :: Puzzle Games",
          "Topic :: Games/Entertainment :: Turn Based Strategy"
      ]
      keywords=["sgsclient", "stratum", "game", "server", "turn", "based",
                "board", "ai", "autonomous", "tictactoe"],
      url="https://python-client.stratumgs.org",
      author="David Korhumel",
      author_email="dpk2442@gmail.com",
      license="MIT",
      packages=find_packages(),
      install_requires=[],
      include_package_data=True,
      zip_safe=False)

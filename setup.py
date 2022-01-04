from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pyoscvideo',
      version='0.2.0',
      author='Sentire',
      author_email='hello@sentire.me',
      description='Synchronized multi-video recorder and player, controllable via OSC',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/Sentire-Dev/pyOscVideo",
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
          "Operating System :: MacOS",
          "Operating System :: POSIX :: Linux",
          "Topic :: Multimedia :: Video :: Capture",
          "Topic :: Multimedia :: Video :: Display",
      ],
      packages=find_namespace_packages(include=['pyoscvideo', 'pyoscvideo.*']),
      keywords='osc video player recorder webcam',
      python_requires='>3.7',
      install_requires=[
          'numpy==1.21.4', 'opencv-python==4.5.4.60', 'PyQt5==5.14.1',
          'PyQt5-sip==12.9.0', 'pyudev==0.22.0', 'six==1.14.0', 'python-osc==1.8.0',
          'PyYAML==5.3.1', 'python-vlc==3.0.12118'
          ],
      entry_points={
          'gui_scripts': [
              'pyoscvideo = pyoscvideo.__main__:main',
              'pyoscvideoplayer = pyoscvideo.player.__main__:main_player'
          ]
      },
      package_data={"": ['*.json']}
      )

from setuptools import setup, find_packages

setup(name='pyoscvideo',
      version='0.1.0',
      packages=find_packages(),
      entry_points={
          'gui_scripts': [
              'pyoscvideo = pyoscvideo.__main__:main'
          ]
      },
      )

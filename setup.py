from setuptools import setup, find_namespace_packages

setup(name='pyoscvideo',
      version='0.1.0',
      packages=find_namespace_packages(include=['pyoscvideo', 'pyoscvideo.*']),
      entry_points={
          'gui_scripts': [
              'pyoscvideo = pyoscvideo.__main__:main'
          ]
      },
      package_data={"": ['*.json']}
      )

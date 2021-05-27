from setuptools import setup, find_namespace_packages

setup(name='pyoscvideo',
      version='0.1.0',
      packages=find_namespace_packages(include=['pyoscvideo', 'pyoscvideo.*']),
      entry_points={
          'gui_scripts': [
              'pyoscvideo = pyoscvideo.__main__:main',
              'pyoscvideoplayer = pyoscvideo.player.__main__:main_player'
          ]
      },
      package_data={"": ['*.json']}
      )

from importlib.metadata import entry_points
from setuptools import setup

setup(name='yatuner',
      version='0.0.1',
      author='Synodic Month, Juni May',
      author_email=' , juni_may@outlook.com',
      description='Yet another auto tuner for compilers.',
      long_description='README.md',
      packages=['yatuner'],
      requires=[
          'GPyOpt', 'GPy', 'numpy', 'matplotlib', 'scipy', 'rich', 'seaborn'
      ],
      license='Mulan PSL v2',
      entry_points={'console_scripts': ['yatuner=yatuner.__main__:main']})

from setuptools import setup, find_packages

setup(
    name = "ArchiveDiff",
    version = "1.0",
    url = 'http://github.com/donovanhide/archivediff',
    license = 'BSD',
    description = "Index Heritrix crawls and find new stuff.",
    author = 'Donovan Hide',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
)


from setuptools import find_packages
from setuptools import setup


setup(
    name='repl_container_python',
    version='1.0.0',
    license='BSD 2-Clause License',
    description='Cyber-dojo REPL runner for Python',
    author='Austin Bingham',
    author_email='austin@sixty-north.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'sanic',
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-sanic',
        ],
    },
)

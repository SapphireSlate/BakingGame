from setuptools import setup, find_packages

setup(
    name="baking-game",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pygame==2.6.1',
        'numpy==1.26.3',
        'scipy==1.11.4',
        'mixbox==1.0.0',
        'moderngl==5.8.2',
        'noise==1.2.2',
    ],
    entry_points={
        'console_scripts': [
            'baking-game=baking_game:main',
        ],
    },
    python_requires='>=3.8',
    author="Robert Craig",
    description="An advanced baking simulation game",
    keywords="game, pygame, baking, simulation",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Games/Entertainment :: Simulation',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
) 
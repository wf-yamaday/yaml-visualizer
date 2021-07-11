from setuptools import setup

install_requires = [
    'PyYAML >= 3.10, < 6',
    'graphviz'
]

setup(
    name='yaml-visualizer',
    description='visualize resources defined by docker-compose.yml.',
    author='wf-yamaday',
    license='MIT License',
    version='0.0.1',
    packages=['viz'],
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'yaml-viz=viz.cli.main:main'
        ],
    },
)

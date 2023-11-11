from setuptools import setup, find_packages

setup(
    name='pic_merger',
    version='0.2',
    install_requires=['Pillow', 'moviepy'],
    packages=find_packages('.'),
    entry_points={
        'console_scripts': [
            'pic-merger = pic_merger.main:cli'
        ]
    },
)

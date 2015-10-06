from setuptools import find_packages
from setuptools import setup


setup(
    name='peersub',
    version='1.1.0',
    description='use peerflix with subtitles',
    long_description='use peerflix with subtitles',
    author='Walid Saad',
    author_email='walid.sa3d@gmail.com',
    url='github.com/walidsa3d/peersub',
        include_package_data=True,
    packages=find_packages(exclude=['test', 'tests']),
    entry_points={"console_scripts": ["peersub=peersub.peersub:main"]},
    classifiers=[
        'License :: Free For Home Use',
        'Natural Language :: English',
        'Programming Language :: Python'
    ]

)

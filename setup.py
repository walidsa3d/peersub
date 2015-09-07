from setuptools import setup
from setuptools import find_packages


setup(
    name='peersub',
    version='0.1',
    description='use peerflix with subtitles',
    long_description='use peerflix with subtitles',
    author='Walid Saad',
    author_email='walid.sa3d@gmail.com',
    url='github.com/walidsa3d/peersub',
    classifiers=[
        'License :: Free For Home Use',
        'Natural Language :: English',
        'Programming Language :: Python'
    ],
    data_files=[(u'', ['README.md', 'LICENSE'])],
    include_package_data=True,
    packages=find_packages(exclude=['test', 'tests']),
)

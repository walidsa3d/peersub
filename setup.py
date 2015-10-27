from setuptools import find_packages
from setuptools import setup


setup(
    name='peersub',
    version='1.2.0',
    description='use peerflix with subtitles',
    long_description='use peerflix with subtitles',
    author='Walid Saad',
    author_email='walid.sa3d@gmail.com',
    url='github.com/walidsa3d/peersub',
        include_package_data=True,
    packages=find_packages(exclude=['test', 'tests']),
    entry_points={"console_scripts": ["peersub=peersub.peersub:main"]},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'
    ]

)

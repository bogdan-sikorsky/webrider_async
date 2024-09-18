from setuptools import setup, find_packages


VERSION = '0.0.5'
DESCRIPTION = 'A simple manager for async requests'


# Setting up
setup(
    name="webrider_async",
    version=VERSION,
    author="Bogdan Sikorsky",
    author_email="<bogdan.sikorsky.dev@gmail.com>",
    url='https://github.com/bogdan-sikorsky/webrider',
    project_urls={
        'Source': 'https://github.com/bogdan-sikorsky/webrider',
        'Documentation': 'https://github.com/bogdan-sikorsky/webrider/README.md',
        "Issues": "https://github.com/bogdan-sikorsky/webrider/issues",
    },

    description=DESCRIPTION,
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords=['python', 'async', 'scraping', 'requests', 'aiohttp', 'asyncio'],

    packages=find_packages(),
    install_requires=['Brotli==1.1.0', 'aiohttp==3.10.5', 'certifi==2024.8.30'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Utilities",
    ],
    python_requires='>=3.8',

    package_data={
        '': ['user_agents_pool.txt'],
    },
)

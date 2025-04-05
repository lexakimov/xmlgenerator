from setuptools import setup, find_packages

setup(
    name='xmlgenerator',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'xmlgenerator=xmlgenerator.bootstrap:main'
        ],
    },
    install_requires=[
        'lxml==5.3.1',
        'xmlschema==3.4.3',
        'Faker==37.0.0',
        'rstr==3.2.2',
        'PyYAML==6.0.2'
    ],
    author='Alexey Akimov',
    author_email='lex.akimov23@gmail.com',
    description='Generates XML documents from XSD schemas',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/lexakimov/xmlgenerator',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

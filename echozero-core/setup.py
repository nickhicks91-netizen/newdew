from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

with open('requirements.txt', 'r', encoding='utf-8') as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith('#')]

setup(
    name='echozero',
    version='0.1.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    author='Resonant Inventor',
    author_email='echo@resonant.ai',
    description='Geometric AI Engine based on Torsion-Warped Lattices',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/echozero-ai/echozero-core',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'echozero-train=train:main',
            'echozero-serve=app:main',
        ],
    },
)

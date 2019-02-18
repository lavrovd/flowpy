from setuptools import setup

setup(name='flowpy',
            version='0.1',
            description='Tools for working with optical flow',
            url='http://github.com/mickaelseznec/flowpy',
            author='Mickaël Seznec',
            author_email='flowpy@seznec.xyz',
            license='MIT',
            packages=['flowpy'],
            install_requires=[
                'numpy',
                'matplotlib',
            ],
            zip_safe=False)


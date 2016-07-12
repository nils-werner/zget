import setuptools
from setuptools.command.sdist import sdist


class Sdist(sdist):
    def run(self):
        self.run_command('compile_catalog')
        sdist.run(self)


if __name__ == "__main__":
    setuptools.setup(
        name='zget',

        version="0.11",

        description='Zeroconf based peer to peer file transfer',
        long_description="""Simply transfer a file over the network using

.. code:: bash

    $ zput file.zip

on the sender and

.. code:: bash

    $ zget file.zip

on the receiver.

Done.""",

        author='Nils Werner',
        author_email='nils.werner@gmail.com',
        url='https://github.com/nils-werner/zget',

        license='MIT',

        packages=setuptools.find_packages(),

        install_requires=[
            'zeroconf<0.17.6',
            'netifaces',
            'progressbar2',
            'requests',
        ],

        setup_requires=[
            'babel'
        ],

        extras_require={
            'docs': [
                'sphinx',
                'sphinxcontrib-napoleon',
                'sphinx_rtd_theme',
                'numpydoc',
            ],
            'tests': [
                'pytest',
                'pytest-cov',
                'pytest-pep8',
                'tox',
                'enum34>=1.1.1',  # otherwise Python 3.5 tox fails
            ],
        },

        tests_require=[
            'pytest',
            'pytest-cov',
            'pytest-pep8',
            'tox',
            'enum34>=1.1.1',  # otherwise Python 3.5 tox fails
        ],

        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'License :: OSI Approved :: MIT License',
            'Topic :: Communications :: File Sharing',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Utilities',
        ],

        entry_points={'console_scripts': [
            'zget=zget.get:cli',
            'zput=zget.put:cli'
        ]},

        cmdclass={'sdist': Sdist},
    )

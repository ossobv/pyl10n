#!/usr/bin/env python
from distutils.core import setup

if __name__ == '__main__':
    long_descriptions = []
    with open('README.rst') as file:
        long_descriptions.append(file.read())

    setup(
        name='pyl10n',
        version='1.0',
        packages=['pyl10n'],
        # Include all locale non-py files in pyl10n as well.
        package_data={'pyl10n': ['locale/README', 'locale/*/LC_*']},
        # Install into '.../share/doc/pyl10n' and include it so we can
        # open it during install.
        data_files=[('share/doc/pyl10n', ['README.rst'])],
        description='Pyl10n is a localization (l10n) library for python',
        long_description=('\n\n\n'.join(long_descriptions)),
        author='Walter Doekes, OSSO B.V.',
        author_email='wjdoekes+pyl10n@osso.nl',
        url='https://github.com/ossobv/pyl10n',
        license='LGPLv3+',
        platforms=['linux'],
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            ('License :: OSI Approved :: GNU Lesser General Public License v3 '
             'or later (LGPLv3+)'),
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Localization',
            'Topic :: Software Development :: Libraries',
        ],
    )

# vim: set ts=8 sw=4 sts=4 et ai tw=79:

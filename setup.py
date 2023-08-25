import setuptools

setuptools.setup(
    name="limekit",
    version="0.1",
    keywords="pyside javascript",
    author="Omega Msiska",
    author_email="omegamsiskah@gmail.com",
    description="Limekit is a wrapper for the cross-platform PySide6 GUI library. It allows developers to create applications for Windows, macOS, and Linux using JavaScript",
    license="GNU",
    packages=setuptools.find_packages(),
    package_data={
        'limekit.framework.handle.theming.misc': ['themes/**'],
        'limekit.framework': ['scripts/**']
    },
    install_requires=[
        'PySide6',
        'qdarkstyle',
        'qt_material',
        'qrcode',
        # 'win11toast',
        'Faker'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License',
        'Operating System :: OS Independent'
    ],
    project_urls={
        'Documentation': 'https://pyqt-fluent-widgets.readthedocs.io/',
        'Source Code': 'https://github.com/mitosisX/Miranda',
        'Bug Tracker': 'https://github.com/mitosisX/Miranda/issues',
    }
)
import setuptools

setuptools.setup(
    name="limekit",
    version="1.0.0",
    keywords="gui lua",
    author="Omega Msiska",
    author_email="omegamsiskah@gmail.com",
    description="Limekit is the first-ever modern lua GUI framework",
    license="GNU",
    packages=setuptools.find_packages(),
    package_data={
        "limekit.framework": ["scripts/*.lua"],  # Explicitly include .lua files
        "limekit.framework.handle.theming.misc": ["themes/*"],  # Non-recursive
    },
    install_requires=[
        "PySide6==6.4.2",
        "qt_material",
        "qdarkstyle",
        "qtmodern",
        "psutil",
        "emoji",
        "playsound",
        "lupa",
        "PyInstaller"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Documentation": "",
    },
)

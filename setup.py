import setuptools

setuptools.setup(
    name="limekit",
    version="2.0.0a1",
    keywords="gui lua",
    author="Omega Msiska",
    author_email="omegamsiskah@gmail.com",
    description="Limekit is the first-ever modern lua GUI framework",
    license="GNU",
    packages=setuptools.find_packages(),
    package_data={
        # Generated runtime: limekit.lua and the LSP stubs (tools/generate_lua.py,
        # tools/generate_stubs.py). limekit/runtime/ and limekit/runtime/lua/ both
        # need __init__.py for find_packages() to see them at all -- without that,
        # these files silently land in no wheel (the exact "works in dev, missing
        # when shipped" defect this branch exists to eliminate).
        "limekit.runtime.lua": ["*.lua", "stubs/*.lua"],
        # Include all .qss files in the themes directory
        "limekit.core.theming": ["themes/misc/themes/*.qss"],
        # You can add more patterns as needed
    },
    include_package_data=True,
    install_requires=[
        "PySide6",
        "lupa",
        "playsound",
        "psutil",
        "emoji",
        "pyqtdarktheme",
        "qdarkstyle",
        "qt_material",
        "qtmodern",
    ],
    extras_require={
        "build": ["PyInstaller"],
        "dev": ["pytest", "pytest-qt", "import-linter"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Documentation": "",
    },
)

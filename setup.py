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
        # Theme assets, shared by the 1.x and 2.0 engines. They used to live
        # under limekit/core/theming/ -- i.e. the 2.0 service reached into the
        # legacy tree for its data. The old key here also named
        # "limekit.core.theming", which find_packages() does not report as a
        # package (no __init__.py), so the pattern matched nothing.
        # Not just *.qss: the misc family also ships .css, icons.rcc and a
        # LINCENSES folder, and qtthemes ships .json palettes.
        "limekit.assets": ["themes/misc/*", "themes/misc/LINCENSES/*",
                           "themes/qtthemes/*"],
    },
    include_package_data=True,
    install_requires=[
        "PySide6",
        "lupa",
        "emoji",
        "pyqtdarktheme",
        "qdarkstyle",
        "qt_material",
    ],
    extras_require={
        "build": ["PyInstaller"],
        "dev": ["pytest", "pytest-qt", "import-linter"],
    },
    entry_points={
        # `python -m limekit <project>` already worked via __main__.py; this
        # just gives it a name on PATH so Limer and users are not obliged to
        # know the -m form.
        "console_scripts": [
            "limekit = limekit.__main__:main",
        ],
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

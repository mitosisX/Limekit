import setuptools

setuptools.setup(
    name="limekit",
    version="1.0",
    keywords="gui lua",
    author="Omega Msiska",
    author_email="omegamsiskah@gmail.com",
    description="Limekit is the first-ever lua GUI framework",
    license="GNU",
    packages=setuptools.find_packages(),
    package_data={
        "limekit.framework.handle.theming.misc": ["themes/**"],
        "limekit.framework": ["scripts/**"],
    },
    install_requires=[
        "PySide6==6.4.2",
        "qt_material",
        "Faker",
        "qdarkstyle",
        "qtmodern",
        "psutil",
        "emoji",
        "xlsxwriter",
        "PySide6-Fluent-Widgets[full]",
        "playsound",
        "lupa",
        "pyecharts",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Documentation": "https://pyqt-fluent-widgets.readthedocs.io/",
    },
)

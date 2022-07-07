from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="metric-vis",
    version="0.0.5",
    license="MIT",
    author="Felix Zhu",
    author_email="zhu.felix@outlook.com",
    description="Metric Visualisation",
    long_description=long_description,
    packages=find_packages(),
    setup_requires=["setuptools_scm"],
    url="https://github.com/felixzhu17/MetricVis",
    install_requires=[
        "plotly",
        "plotly-express",
        "pandas",
        "numpy",
        "nbformat",
    ],
)

from setuptools import setup, find_packages

setup(
    name="bbox-exporter",
    version="1.0.0",
    description="Prometheus exporter for Bbox router",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "prometheus-client>=0.19.0",
        "requests>=2.31.0",
        "urllib3>=2.0.0",
    ],
    entry_points={
        'console_scripts': [
            'bbox-exporter=bbox_exporter.main:main',
        ],
    },
    python_requires='>=3.7',
)

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vtx_emulator",
    version="0.1.0",
    author="Volodymyr Kopytsia",
    author_email="v.kopitsa@gmail.com",
    description="Python emulator for VTX devices with SmartAudio protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vkopitsa/vtx_emulator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Embedded Systems",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "vtx_emulator=main_port:run_emulator",
        ],
    },
)

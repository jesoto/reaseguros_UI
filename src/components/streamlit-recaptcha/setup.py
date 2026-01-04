import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="streamlit-recaptcha",
    version="0.1.0",
    author="Machine Learning Engineer Team",
    author_email="ml-engineer-team@empresa.com",
    description="Componente de reCAPTCHA para Streamlit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tu-usuario/streamlit-recaptcha",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "streamlit>=1.0.0",
        "requests>=2.25.0"
    ]
)
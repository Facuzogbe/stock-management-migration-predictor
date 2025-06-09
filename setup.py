from setuptools import setup, find_packages

setup(
    name="stock_manager",
    version="0.1",
    package_dir={"": "src"},  # Indica que los paquetes están en src/
    packages=find_packages(where="src"),  # Busca paquetes en src/
    install_requires=[
        "flask",
        "flask-sqlalchemy",
        "pandas",
        "scikit-learn",
        "statsmodels",
    ],
    python_requires=">=3.9",
)
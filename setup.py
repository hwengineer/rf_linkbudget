import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='rf-linkbudget',
                 version='1.1.6',
                 description='A simple rf-linkbudget calculation tool',
                 url='https://github.com/hwengineer/rf_linkbudget',
                 author='Alexander Ott',
                 author_email='alexander.ott.ottale@gmail.com',
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 license='MIT',
                 packages=setuptools.find_packages(),
                 classifiers=["Programming Language :: Python :: 3",
                              "License :: OSI Approved :: MIT License",
                              "Operating System :: OS Independent", ],
                 python_requires='>=3.5',
                 zip_safe=False)

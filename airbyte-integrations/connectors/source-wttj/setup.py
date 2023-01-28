#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.2", "algoliasearch"]

TEST_REQUIREMENTS = [
    "pytest~=6.2",
    "source-acceptance-test",
]

setup(
    name="source_wttj",
    description="Source implementation for Wttj.",
    author="Elliot Trabac",
    author_email="elliot.trabac1@gmail.com",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)

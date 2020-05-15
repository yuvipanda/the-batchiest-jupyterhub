from setuptools import setup, find_packages

setup(
    # Maybe not this name?
    name='the-batchiest-jupyterhub',
    version='0.1',
    author='Yuvi Panda',
    author_email='yuvipanda@gmail.com',
    license='3 Clause BSD',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # All packages we support in the distro
        'jupyterhub==1.1.0',
        'jupyterhub-dummyauthenticator==0.3.1',
        'jupyterhub-nativeauthenticator==0.0.5',
        'jupyterhub-ldapauthenticator==1.3.0',
        'jupyterhub-tmpauthenticator==0.6',
        'oauthenticator==0.10.0',
        'jupyterhub-idle-culler==1.0',
        'jupyterhub-traefik-proxy==0.1.*',
        'batchspawner @ git+https://github.com/jupyterhub/batchspawner.git@33b4a7b5134c3645911f9adfb3c97839cc76e668',

        'passlib',
        'backoff',
        'requests',
        'jinja2'
    ]
)

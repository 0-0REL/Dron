from setuptools import find_packages, setup

package_name = 'sim_dron'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/modelos', [
            'modelos/deploy.prototxt',
            'modelos/res10_300x300_ssd_iter_140000_fp16.caffemodel'
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rodrigo',
    maintainer_email='rodrigo12337@outlook.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'vision = sim_dron.vision:main',
        ],
    },
)

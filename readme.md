# BootBaker

BootBaker is a script designed for testing FreeBSD across multiple architectures, file systems, and disk-partitioning schemes. The script facilitates the testing of booting for all architecture combinations supported in the first and second-tier support, providing a report on broken combinations and expected functionality.

## Features

* **Versatile Testing** : Test booting for various architecture combinations to ensure cross-architecture compatibility.
* **Linux Boot Support (WIP)** : Includes Linux Boot support using Linux EFI shim (EDK) II for amd64 and arm64.
* **Automatic Detection of Broken Combinations**: Helps in detecting issues where commits in one architecture break the bootloader for other architectures.

Further integration with existing build infrastructure (e.g., Jenkins or GitHub Actions) is under exploration to generate comprehensive test result summaries.

## How it Works

BootBaker fetches various FreeBSD images, builds resources (modified qemu images), and tests them for boot. If the qemu image successfully boots, it indicates that the combination of architecture, file system, boot interface, and encryption is functioning correctly.

## Installation

To Build the package to run as bootbaker.
```sh
pip install --editable . 
```

## Getting Started


## Open Items
TODO:
* Create a new Resource Manger Class that parallely executes build and testing for bunch of combination
* Add instructions to use this package
* Enrich with support of more combinations to use
* Work towards getting this published as pip package or a port for FreeBSD(good for exposure to ports)
* Work on presenting this work to community
* Work towards optimizing this for CI/CD Pipeline so it could be utilised on commit basis
* Work on writing good documentation so that developers can include this as a tool in their arsenal for 
  bootloader related stuff


## Contributions

Contributions are welcomed! If you encounter any issues or have ideas for improvement, please feel free to submit a pull request.
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
pip3 install --editable . 
```

## Getting Started

#### 1. Run a Basic Test Command for specific combination
```bash
bootbaker run -a amd64:amd64 -i gpt -f ufs -e none -v
```

#### 2. Options Explained
```txt
$ bootbaker run --help
Usage: bootbaker run [OPTIONS]

Options:
  -c, --configfile FILENAME       Config file to run bootbaker
  -s, --src PATH                  path to freebsd source tree
  -a, --arch [amd64:amd64|arm64:aarch64|arm:armv7|riscv:riscv64|powerpc:powerpc64]
                                  architecture name
  -i, --interface [gpt|mbr|*]     interface name
  -f, --filesystem [ufs|zfs|*]    filesystem name
  -e, --encryption [geom|geli|none]
                                  encryption strategy
  -b, --build-only                Only builds bootloader
  -t, --test-only                 Only tests bootloader
  -v, --verbose                   sets verbosity of output
  --help                          Show this message and exit.
```

#### 3. Running using Custom Config File
```bash
bootbaker run -c custom_config.yaml
```

```yaml
# example config
recipe_1:
  arch: "amd64:amd64"
  machine_arch: "amd64"
  machine_combo: "amd64"

  # optional parameters
  freebsd_version: "13.2"
  img_flavor: "bootonly.iso"
  img_url: "FreeBSD-13.0-RELEASE-amd64-bootonly.iso"
  regex_combination: ["*-*-none"]
  # above expression evaluates to following combinations
  # regex_combination = {"ufs-gpt-none","ufs-mbr-none","zfs-gpt-none", "zfs-mbr-none"}
  # note there is a internal filter that filters out none working combinations
recipe_2:
  arch: "arm64:aarch64"
  regex_combination: ["*-gpt-none"]
recipe_3:
  arch: "riscv:riscv64"
  regex_combination: ["*-gpt-none"]
```

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
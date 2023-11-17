"""
* --------------------------------------------------------------------
* @file    
* @brief   default config for running
* @author  smk (smk@it.ca)
* @version 20231116
* @license BSD3
* @bugs    No know bugs
* --------------------------------------------------------------------
"""

# Defaults
VALID_ARCH = ["amd64:amd64", "arm64:aarch64", "arm:armv7", "riscv:riscv64", "powerpc:powerpc64"]
VALID_INTERFACES = ["gpt", "mbr"]
VALID_FILE_SYSTEMS = ["ufs", "zfs"]
VALID_ENCRYPTION = ["geom", "geli", "none"]
STAND_TEST_ROOT = "/home/smk/stand-test-root"
SRCTOP = "/home/smk/freebsd-src"

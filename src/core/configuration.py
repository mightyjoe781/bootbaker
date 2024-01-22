from src.config import STAND_TEST_ROOT
import os


# Config class object represents a set of config to run by program
class Config:
    URLBASE = "https://download.freebsd.org/ftp/releases"
    VALID_ARCHES = ["amd64:amd64", "arm64:aarch64", "arm:armv7", "riscv:riscv64",
                     "powerpc:powerc64", "arm:arm", "arm:armv6", "powerpc:powerpc"]
    VALID_FILESYSTEMS = ["ufs", "zfs", "ffs"]
    VALID_INTERFACES = ["gpt", "mbr"]
    VALID_ENCRYPTIONS = ["geom","geli","none"]
    SCRIPT_DIR = f"{STAND_TEST_ROOT}/script"
    LOG_DIR = f"{STAND_TEST_ROOT}/logs"
    target_string = "RC COMMAND RUNNING -- SUCCESS!!!"

    def __init__(self, arch, filesystem, interface, flavor, img_file, img_url, port, encryption="none", version="13.2", recipe={}):
        # validation
        self.validate_arch(arch)
        self.validate_filesystem(filesystem)
        self.validate_interface(interface)
        self.validate_encryption(encryption)

        self.arch = arch
        self.machine = arch.split(":")[0]
        self.machine_arch = arch.split(":")[1]
        self.machine_combo = self.get_machine_combo(self.machine, self.machine_arch)
        self.filesystem = filesystem
        self.interface = interface
        self.encryption = encryption
        self.version = version
        self.flavor = flavor or self.get_flavor(self.arch)
        self.img_file = img_file or self.get_image_file(self.machine_combo, self.flavor, self.version)
        self.img_url = img_url or self.get_img_url(self.machine, self.machine_arch, self.version, self.img_file)
        self.port = port
        self.identifier = self.get_identifier_name()
        self.recipe = recipe

        # config files
        self.rc_conf = self.get_rc_conf()
        self.loader_conf = self.get_loader_conf()
        self.fstab_conf = self.get_fstab_conf()

        # for testing
        self.script_file = f"{self.identifier}.sh"
        self.script_dir = os.path.join(self.SCRIPT_DIR, self.machine_combo)
        self.log_path = os.path.join(self.LOG_DIR, self.machine_combo)
        self.log_file = os.path.join(self.log_path, self.script_file.replace('.sh', '.log'))
        self.setup_dirs()

    def setup_dirs(self):
        os.makedirs(self.LOG_DIR,exist_ok=True)

    def get_machine_combo(self, m, ma):
        return f"{m}-{ma}" if m != ma else ma

    def get_flavor(self,arch):
        return "GENERIC.img" if arch in ["arm:armv7", "arm:armv6", "arm:arm"] else "bootonly.iso"

    def get_image_file(self, mc, flavor, version):
        return f"FreeBSD-{version}-RELEASE-{mc}-{flavor}"
    
    def get_img_url(self, m, ma, version, img_file):
        return f"{self.URLBASE}/{m}/{ma}/ISO-IMAGES/{version}/{img_file}.xz"

    def get_identifier_name(self):
        return f"FreeBSD-{self.version}-{self.machine_combo}-{self.filesystem}-{self.interface}-{self.encryption}"
    
    def get_rc_conf(self):
        return f"""
#!/bin/sh
sysctl machdep.bootmethod
echo "RC COMMAND RUNNING -- SUCCESS!!!"
halt -p
        """

    def get_loader_conf(self):
        return f"""
comconsole_speed=115200
autoboot_delay=2
zfs_load="YES"
boot_verbose=yes
kern.cfg.order="acpi,fdt"
"""

    def get_fstab_conf(self):
        zfs_pool = "tank"
        return f"{zfs_pool} / zfs rw 1 1" if self.filesystem == "zfs" else "/dev/ufs/root / ufs rw 1 1"

    def validate_arch(self, arch):
        if arch not in self.VALID_ARCHES:
            raise ValueError(f"Invalid arch: {arch}. Valid arches are: {', '.join(self.VALID_ARCHES)}")

    def validate_filesystem(self, filesystem):
        if filesystem not in self.VALID_FILESYSTEMS:
            raise ValueError(f"Invalid filesystem: {filesystem}. Valid filesystems are: {', '.join(self.VALID_FILESYSTEMS)}")

    def validate_interface(self, interface):
        if interface not in self.VALID_INTERFACES:
            raise ValueError(f"Invalid interface: {interface}. Valid interfaces are: {', '.join(self.VALID_INTERFACES)}")

    def validate_encryption(self, encryption):
        if encryption not in self.VALID_ENCRYPTIONS:
            raise ValueError(f"Invalid encryption: {encryption}. Valid encryptions are: {', '.join(self.VALID_ENCRYPTIONS)}")

    def __str__(self):
        return f"Config({', '.join(f'{attr}={value}' for attr, value in vars(self).items())})"
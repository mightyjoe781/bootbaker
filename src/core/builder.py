from src.config import STAND_TEST_ROOT
from src.config import SRCTOP
from src.core.configuration import Config
from src.utils.freebsd_utils import FreeBSDUtils
import urllib.request
import xz
import shutil
import subprocess
import os

class ConfigBuilder:
    BIOS_DIR = f"{STAND_TEST_ROOT}/bios"
    CACHE_DIR = f"{STAND_TEST_ROOT}/cache"
    IMAGE_DIR = f"{STAND_TEST_ROOT}/image"
    SCRIPT_DIR = f"{STAND_TEST_ROOT}/script"
    TREE_DIR = f"{STAND_TEST_ROOT}/tree"
    VIRTUAL_DEVICE_ID = 3

    def __init__(self, config: Config):
        self.config = config
        self.machine_combo = self.config.machine_combo
        self.machine_arch = self.config.machine_arch
        self.img_file = self.config.img_file
        self.img_url = self.config.img_url
        self.rc_conf = self.config.rc_conf
        self.loader_conf = self.config.loader_conf
        self.override_kernel = False
        self.identifier = self.config.identifier

    def build_resource(self):
        self.setup_dirs()
        self.update_freebsd_img_cache()
        self.build_freebsd_minimal_trees()
        self.build_freebsd_test_trees()
        self.build_freebsd_esps()
        self.build_freebsd_images()
        self.build_freebsd_scripts()

    def setup_dirs(self):
        dirs = [self.BIOS_DIR, self.CACHE_DIR, self.IMAGE_DIR, self.SCRIPT_DIR, self.TREE_DIR]
        for dir in dirs:
            os.makedirs(dir, exist_ok=True)
    
    def update_freebsd_img_cache(self):

        # check file exists in cache
        file_path = os.path.join(self.CACHE_DIR, self.img_file)
        if os.path.exists(file_path):
            print(f"File {self.img_file} Exists!")
            return

        # fetch file and uncompress using xz
        print(f"File doesn't exists fetching ...")
            # Download the image
        xz_file_path = f"{file_path}.xz"
        if os.path.exists(xz_file_path):
            # compressed file exists but needs to be unpacked
            with xz.open(xz_file_path) as f:
                with open(file_path, 'wb') as fout:
                    shutil.copyfileobj(f, fout)
            return
        
        # fetch file
        urllib.request.urlretrieve(self.img_url, xz_file_path)
        # Extract the image
        with xz.open(xz_file_path) as f:
            with open(file_path, 'wb') as fout:
                shutil.copyfileobj(f, fout)
        # os.remove(xz_file_path)


    def build_freebsd_minimal_trees(self):
        tree = f"{self.TREE_DIR}/{self.machine_combo}/freebsd"

        # cleanup & recreate tree
        # note if sudo creates the tree, then shutil doesn't work properly and ignore_error bypasses that
        # should include a check here
        shutil.rmtree(tree, ignore_errors=True)
        os.makedirs(tree,exist_ok=True)

        # create required dirs
        dirs = ["boot/kernel", "boot/defaults", "boot/lua", "boot/loader.conf.d", "sbin", "bin", "lib", "libexec", "etc", "dev"]
        for directory in dirs:
            full_path = os.path.join(tree, directory)
            os.makedirs(full_path, exist_ok=True)

        # TODO: fix this
        # link the /usr
        # link_path = os.path.join(tree, "usr")
        # os.symlink(tree, link_path)
        # subprocess.run(f"ln -s . {link_path}", shell=True)

        # extract/copy required binaries
        bins = [
            "sbin/reboot", "sbin/halt", "sbin/init", "bin/sh", "sbin/sysctl",
            "lib/libncursesw.so.9", "lib/libc.so.7", "lib/libgcc_s.so.1", "lib/libedit.so.8", "libexec/ld-elf.so.1"
        ]
        if self.config.flavor == "bootonly.iso":
            cmd = ["tar", "-C", tree, "-xf", f"{self.CACHE_DIR}/{self.img_file}"] + bins
            subprocess.run(cmd)
        else :
            # implement mount logic
            pass

        # write rc, loader files
        with open(os.path.join(tree, "etc/rc"), 'w') as rc_file:
            rc_file.write(self.rc_conf)

        with open(os.path.join(tree, "boot/loader.conf"), 'w') as loader_file:
            loader_file.write(self.loader_conf)

        # override kernel setup
        if not self.override_kernel :
            override_files = ["boot/kernel/kernel", "boot/kernel/acl_nfs4.ko", "boot/kernel/cryptodev.ko", "boot/kernel/zfs.ko", "boot/kernel/geom_eli.ko", "boot/device.hints"]
            # script || true -> always pass
            override_cmd = ["tar", "-C", tree, "-xf", f"{self.CACHE_DIR}/{self.img_file}"] + override_files
            subprocess.run(override_cmd)
            print(f"Kernel Override Ignored!")
        else:
            # implement kernel override code
            pass

    def build_freebsd_test_trees(self):
        test_dir = os.path.join(self.TREE_DIR, self.machine_combo, "test-stand")
        os.makedirs(test_dir, exist_ok=True)

        mtree_cmd = ["mtree", "-deUW", "-f", f"{SRCTOP}/etc/mtree/BSD.root.dist", "-p", test_dir]
        subprocess.run(mtree_cmd, check=True)

        buildenv_cmd = ["cd", f"{SRCTOP}/stand", "&&", 
                        "SHELL='make -j 100 all'", "make", "buildenv", 
                        f"TARGET={self.config.machine}",
                        f"TARGET_ARCH={self.config.machine_arch}"]
        buildinstall_cmd = ["cd", f"{SRCTOP}/stand", "&&", 
                        f"SHELL=\"make install DESTDIR='{test_dir}' MK_MAN=no MK_INSTALL_AS_USER=yes WITHOUT_DEBUG_FILES=yes\"",
                        "make",
                        "buildenv",
                        f"TARGET={self.config.machine}",
                        f"TARGET_ARCH={self.config.machine_arch}"]
        try:
            buildenv_cmd_str = " ".join(buildenv_cmd)
            buildinstall_cmd_str = " ".join(buildinstall_cmd)
            os.system(buildenv_cmd_str)
            os.system(buildinstall_cmd_str)
        except:
            raise Exception("Could not Build Env")

        subprocess.run(["rm", "-rf", f"{test_dir}/bin"], check=True)
        subprocess.run(["rm", "-rf", f"{test_dir}/[ac-z]*"], check=True)

    def build_freebsd_esps(self):
        test_dir = os.path.join(self.TREE_DIR, self.machine_combo, "test-stand")
        esp_dir = os.path.join(self.TREE_DIR, self.machine_combo, "freebsd-esp")

        shutil.rmtree(esp_dir, ignore_errors=True)
        os.makedirs(esp_dir)
        os.makedirs(os.path.join(esp_dir, "efi", "boot"))

        boot_efi = FreeBSDUtils.get_boot_ufi(self.machine_arch)

        src_path = os.path.join(test_dir, "boot", "loader.efi")
        dst_path = os.path.join(esp_dir, "efi", "boot", boot_efi)
        shutil.copy(src_path, dst_path)

    def build_esp(self, esp, src):
        # -t msdos : fat32 filesystem
        # -o fat_type=32 : 32 or 64 bit fat file
        # -o sectors_per_cluster=1 : each cluster will have 1 sector
        # -s 100m : size of fs to be 100MB
        cmd = f"makefs -t msdos -o fat_type=32 -o sectors_per_cluster=1 -o volume_label=EFISYS -s 100m {esp} {src}"
        subprocess.run(cmd, shell=True)

    def build_fs(self, fs_file, dir1, dir2):
        #- -t ffs : fast file system
        #- -B little : little_endian format
        #- -s 200m : size of fs to be created 200MB
        #- -o label=root : specifies the label as root
        #- copies over content of the dir1, dir2 into the fs indicated
        if self.config.filesystem == "zfs":
            zfs_pool = "tank"
            cmd = f"makefs -t zfs -s 200m -o poolname={zfs_pool} -o bootfs={zfs_pool} -o rootpath=/ {fs_file} {dir1} {dir2}"
        else:
            cmd = f"makefs -t ffs -B little -s 200m -o label=root {fs_file} {dir1} {dir2}"
        
        subprocess.run(cmd, shell=True, check=True)

    def build_image(self, esp_file, fs_file, img_file):
        bi = self.config.interface
        if bi == "mbr":
            cmd = f"mkimg -s {bi} -p efi:={esp_file} -p freebsd:={fs_file} -o {img_file}"
        else:
            cmd = f"mkimg -s {bi} -p efi:={esp_file} -p freebsd-{self.config.filesystem}:={fs_file} -o {img_file}"
        subprocess.run(cmd, shell=True, check=True)

    def build_freebsd_images(self):
        src = os.path.join(self.TREE_DIR, self.machine_combo, "freebsd-esp")
        dir = os.path.join(self.TREE_DIR, self.machine_combo, "freebsd")
        fstab_dir = os.path.join(self.TREE_DIR, self.machine_combo, "test-stand")
        self.esp_file = os.path.join(self.IMAGE_DIR, self.machine_combo, f"freebsd-{self.identifier}.esp")
        self.fs_file = os.path.join(self.IMAGE_DIR, self.machine_combo, f"freebsd-{self.identifier}.{self.config.filesystem}")
        self.img_file = os.path.join(self.IMAGE_DIR, self.machine_combo, f"freebsd-{self.identifier}.img")
        
        # mkdirs
        os.makedirs(os.path.join(self.IMAGE_DIR, self.machine_combo),exist_ok=True)
        os.makedirs(os.path.join(fstab_dir, "etc"),exist_ok=True)
        
        # fstab file
        with open(os.path.join(fstab_dir, "etc/fstab"), 'w') as fstab_file:
            fstab_file.write(self.config.fstab_conf)

        self.build_esp(self.esp_file, src)
        self.build_fs(self.fs_file, dir, fstab_dir)
        self.build_image(self.esp_file, self.fs_file, self.img_file)

    def build_freebsd_scripts(self):
        bios_code = os.path.join(self.BIOS_DIR, f"edk2-{self.machine_combo}-code.fd")
        bios_var = os.path.join(self.BIOS_DIR, f"edk2-{self.machine_combo}-var.fd")

        if self.config.machine == "amd64":
            shutil.copy("/usr/local/share/qemu/edk2-x86_64-code.fd", bios_code)
            shutil.copy("/usr/local/share/qemu/edk2-i386-vars.fd", bios_var)
        else:
            pass

        # make script dirs
        os.makedirs(os.path.join(self.SCRIPT_DIR, self.machine_combo), exist_ok=True)
        self.script = os.path.join(self.SCRIPT_DIR, self.machine_combo, self.identifier)+".sh"
        qemu_recipe = FreeBSDUtils.get_qemu_recipe(self.config.machine, self.config.machine_arch,
                                     self.config.filesystem, self.img_file, bios_code, bios_var, self.config.port)
        with open(self.script, 'w') as s:
            s.write(qemu_recipe)
    
    def __str__(self):
        return f"Config({', '.join(f'{attr}={value}' for attr, value in vars(self).items())})"
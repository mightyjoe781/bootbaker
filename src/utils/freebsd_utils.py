class FreeBSDUtils:

    def __init__(self):
        pass

    def get_qemu_bin(ma):
        qemu_bin_map = {
            "amd64" : "/usr/local/bin/qemu-system-x86_64",
            "i386" : "/usr/local/bin/qemu-system-i386",
            "armv7" : "/usr/local/bin/qemu-system-arm",
            "aarch64" : "/usr/local/bin/qemu-system-aarch64",
            "powerpc" : "/usr/local/bin/qemu-system-ppc",
            "powerpc64" : "/usr/local/bin/qemu-system-ppc64",
            "riscv64" : "/usr/local/bin/qemu-system-riscv64",
            "powerpc64le" : "/usr/local/bin/qemu-system-ppc64le"
        }
        if ma not in qemu_bin_map.keys():
            return None
        return qemu_bin_map[ma]

    @staticmethod
    def get_boot_ufi(machine_arch):
        boot_efi_name = {
            "amd64" : "bootx64.efi",
            "i386" : "bootia32.efi",
            "armv7" : "bootarm.efi",
            "aarch64" : "bootaa64.efi",
            "powerpc" : "bootppc64.efi",
            "powerpc64" : "bootppc64.efi",
            "riscv64" : "bootriscv64.efi",
            "powerpc64le" : "bootppc64le.efi"
        }
        if machine_arch not in boot_efi_name.keys():
            return None
        return boot_efi_name[machine_arch]

    @staticmethod
    def get_qemu_recipe(self,m, ma, fs, img, bios_code, bios_vars, port):
        qemu_bin = self.get_qemu_bin(ma)
        if ma == "amd64":
            script = f"""
            {qemu_bin} -nographic -m 512M \
            -drive file={img},if=none,id=drive0,cache=writeback,format=raw \
            -device virtio-blk,drive=drive0,bootindex=0 \
            -drive file={bios_code},format=raw,if=pflash \
            -monitor telnet::{port},server,nowait \
            -serial stdio $*
            """
        elif ma == "arm64":
            script = f"""
            {qemu_bin} -m 512M -cpu cortex-a57 -M virt,gic-version=3 -nographic  \
            -drive file={img},if=none,id=drive0 \
            -drive file={bios_code},format=raw,if=pflash,readonly=on \
            -drive file={bios_vars},format=raw,if=pflash \
            -device virtio-blk-device,drive=drive0 \
            -monitor telnet::{port},server,nowait \
            -serial stdio $*]]
            """

        return script

# Attribution and licenses

This is an unofficial device-specific build recipe for OrangeFox Recovery. The OrangeFox project documents GPL version 3 or later licensing for its recovery sources and vendor build tree. Its build guide covers disclosure of modified sources when distributing an unofficial public build. [OrangeFox build guide](https://wiki.orangefox.tech/dev/building#copyright) · [GNU GPL version 3](https://www.gnu.org/licenses/gpl-3.0.html)

- Recovery sources and build tooling come from the OrangeFox project. [Recovery source](https://gitlab.com/OrangeFox/bootable/Recovery) · [Vendor build tree](https://gitlab.com/OrangeFox/vendor/recovery) · [Sync tooling](https://gitlab.com/OrangeFox/sync)
- The Samsung Exynos 2100 device configuration and matching `p3s` kernel and module inputs come from xfwdrev's upstream device tree. [Upstream Exynos device tree](https://github.com/xfwdrev/android_device_samsung_exynos2100_ofox)
- The device-tree maintainer identifies the ChicletKernel source repository and its recovery build option. The release records the exact device-tree prebuilt revision and kernel binary SHA-256. The kernel source repository is the upstream maintainer's published source location. An exact kernel source commit for the supplied prebuilt is unconfirmed. [Kernel source](https://github.com/xfwdrev/android_kernel_samsung_ex2100) · [Pinned prebuilt tree](https://github.com/xfwdrev/android_device_samsung_exynos2100_ofox/tree/7c020092214705138b7fb1331cf6474f24080a2e)

[`sources.env`](sources.env) records the selected upstream revisions, and [`patches/`](patches/) contains the device changes. Each upstream component retains its own copyright notices and applicable license terms.

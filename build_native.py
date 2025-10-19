import argparse
import os
import platform
import subprocess
import sys
import time

from xmlgenerator import __version__

DEFAULT_MAIN_SCRIPT = "xmlgenerator/bootstrap.py"
DEFAULT_OUTPUT_FILENAME_BASE = "xmlgenerator"
DEFAULT_OUTPUT_DIR = "dist_native"
DEFAULT_EXTRA_ENVS = "CCFLAGS=-Oz -g0 -w"

BUILD_TIME = str(int(time.time()))
FILE_VERSION = f"{BUILD_TIME[-4]}.{BUILD_TIME[-3]}.{BUILD_TIME[-2]}.{BUILD_TIME[-1]}"

PLATFORM_ALIASES = {
    "darwin": "macos",
    "mac": "macos",
    "macos": "macos",
    "osx": "macos",
    "win32": "windows",
    "cygwin": "windows",
    "windows": "windows",
    "linux": "linux",
    "linux2": "linux",
}

ARCH_ALIASES = {
    "x86_64": "amd64",
    "amd64": "amd64",
    "x64": "amd64",
    "i686": "x86",
    "i386": "x86",
    "arm64": "arm64",
    "aarch64": "arm64",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build xmlgenerator into a native executable via Nuitka",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--artifact-name",
        help=(
            "Final artifact filename. "
            "Provide an extension manually for non-standard packages."
        ),
        default=None,
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for build artifacts",
        default=DEFAULT_OUTPUT_DIR,
    )
    parser.add_argument(
        "--target-platform",
        help=(
            "Target platform name (linux/windows/macos). "
            "Defaults to the current operating system."
        ),
        default=None,
    )
    parser.add_argument(
        "--target-arch",
        help=(
            "Target architecture name (for example, amd64, arm64). "
            "Defaults to the automatically detected value."
        ),
        default=None,
    )
    parser.add_argument(
        "--extra-envs",
        help=f"Target architecture name (for example, amd64, arm64). Default: {DEFAULT_EXTRA_ENVS}.",
        default=DEFAULT_EXTRA_ENVS,
    )
    parser.add_argument(
        "--extra-opts",
        help="Custim Nuitka options.",
        default=None,
    )

    return parser.parse_args()


def normalize_platform_name(platform_hint: str | None) -> str:
    if platform_hint:
        key = platform_hint.strip().lower()
    else:
        key = sys.platform.lower()
    return PLATFORM_ALIASES.get(key, key)


def normalize_architecture(arch_hint: str | None) -> str:
    if arch_hint:
        key = arch_hint.strip().lower()
    else:
        key = platform.machine().lower()
    return ARCH_ALIASES.get(key, key)


def ensure_output_filename(artifact_name: str | None, platform_name: str) -> str:
    filename = (artifact_name or DEFAULT_OUTPUT_FILENAME_BASE).strip() or DEFAULT_OUTPUT_FILENAME_BASE
    if platform_name == "windows" and not filename.lower().endswith(".exe"):
        filename = f"{filename}.exe"
    return filename


def write_step_output(name: str, value: str) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output and value:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")


def main() -> None:
    args = parse_args()

    target_platform = normalize_platform_name(args.target_platform)
    target_arch = normalize_architecture(args.target_arch)
    output_dir = args.output_dir
    output_filename = ensure_output_filename(args.artifact_name, target_platform)
    artifact_path = os.path.join(output_dir, output_filename)
    extra_opts = args.extra_opts.split() if args.extra_opts is not None else []
    extra_envs = args.extra_envs.split(';')

    print(f"Target platform: {target_platform}, architecture: {target_arch}")
    print(f"extra_opts: {extra_opts}")
    print(f"extra_envs: {extra_envs}")
    print()

    command = [
        sys.executable, "-m", "nuitka",

        # Options:
        "--python-flag=no_asserts,no_docstrings,no_site,static_hashes",
        "--mode=onefile",

        # Control the inclusion of modules and packages in result:

        # Control the following into imported modules:

        # Onefile options:
        "--onefile-tempdir-spec={CACHE_DIR}/{PRODUCT}/{VERSION}",

        # Data files:

        # Metadata support:

        # DLL files:

        # Control the warnings to be given by Nuitka:
        "--assume-yes-for-downloads",

        # Immediate execution after compilation:

        # Compilation choices:

        # Output choices:
        "--output-filename=" + output_filename,
        "--output-dir=" + output_dir,
        "--remove-output",

        # Deployment control:
        "--no-deployment-flag=self-execution",

        # Environment control:

        # Debug features:
        "--no-debug-c-warnings",

        # Nuitka Development features:

        # Backend C compiler choice:
        "--lto=yes",
        # "--static-libpython=yes",     # Use static link library of Python
        # "--static-libpython=no",

        # Cache Control:

        # PGO compilation choices:

        # Tracing features:
        #"--report=report.xml",

        # General OS controls:

        # Windows specific controls:

        # macOS specific controls:

        # Linux specific controls:

        # Binary Version Information:
        "--product-name=xmlgenerator",
        "--product-version=" + __version__,
        "--file-version=" + FILE_VERSION,

        # Plugin control:
        "--enable-plugin=pylint-warnings",
        "--enable-plugin=no-qt",

        # Cross compilation:

        # Plugin options of 'anti-bloat' (categories: core):
        "--show-anti-bloat-changes",
        "--noinclude-pytest-mode=nofollow",
        "--noinclude-setuptools-mode=nofollow",
        "--noinclude-default-mode=warning",

        # Plugin options of 'playwright' (categories: package-support):

        # Plugin options of 'spacy' (categories: package-support):
    ]

    command.extend(extra_opts)
    command.append(DEFAULT_MAIN_SCRIPT)

    print("Running Nuitka with the following command:")
    print(" ".join(command))
    print("-" * 30)

    try:
        extended_env = os.environ.copy()
        for pair in extra_envs:
            if not pair:
                continue
            key, value = pair.split('=', 1)
            extended_env[key] = value

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env=extended_env
        )

        print("--- Nuitka output --- ")
        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                sys.stdout.write(line)
                sys.stdout.flush()
            process.stdout.close()

        return_code = process.wait()
        print("-" * 60)

        if return_code == 0:
            print(f"Build succeeded! Executable: {artifact_path}")
            write_step_output("artifact_path", artifact_path)
        else:
            print(f"Nuitka build failed (exit code {return_code})")
            sys.exit(return_code)
    except FileNotFoundError:
        print(
            f"Error: Unable to run '{sys.executable} -m nuitka'. "
            "Ensure Nuitka is installed in your environment."
        )
        sys.exit(1)
    except Exception as exc:
        print(f"Unexpected error occurred: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

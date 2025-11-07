Import("env")

package_json = env.File("package.json")

#
# automatically generate `include/version.h`
#
def build_version_h(target, source, env):
    import json

    version = None
    with open(str(source[0]), "r") as f:
        version = json.load(f)["version"]

    with open(str(target[0]), "w") as h:
        h.write('// Automatically generated -- do not modify\n')
        h.write('// Modify `package.json` instead.\n\n')
        h.write('#define VERSION "' + version + '"\n')

    return None

#
# automatically generate `include/uhrtype.h`
#
def build_uhrtype_h(target, source, env):
    import glob

    with open(str(target[0]), "w") as h:
        h.write('// Automatically generated -- do not modify\n\n')
        for file in glob.glob("include/Uhrtypes/*.hpp"):
            h.write('#include "' + file.replace('include/','') + '"\n')

    return None

env.Command(
    target="include/uhrtype.gen.h",
    source=package_json,
    action=build_uhrtype_h
)

env.Command(
    target="include/version.gen.h",
    source=package_json,
    action=build_version_h
)

#
# automatically build web page
#

npm_ci = env.Command(
    target="node_modules/.package-lock.json",
    source="package-lock.json",
    action="npm ci --silent"
)

def run_grunt_build(target, source, env):
    import os
    import shutil
    import subprocess

    env_vars = os.environ.copy()
    env_vars["PIO_ENV_NAME"] = env["PIOENV"]

    npx_binary = shutil.which("npx", path=env_vars.get("PATH"))

    if os.name == "nt" and npx_binary is None:
        # When PlatformIO is executed from the VS Code extension on
        # Windows, the PATH that is propagated to this helper script may
        # not contain the default npm installation directory.  `npx.cmd`
        # is the actual executable that needs to be invoked on Windows,
        # therefore we try to resolve it explicitly.
        npx_binary = shutil.which("npx.cmd", path=env_vars.get("PATH"))

    if npx_binary is None:
        print("Error: unable to locate 'npx'. Please ensure that Node.js is installed and available in PATH.")
        return 1

    result = subprocess.run(
        [npx_binary, "--no-install", "grunt", "build"],
        cwd=env.subst("$PROJECT_DIR"),
        env=env_vars,
        check=False,
    )

    return result.returncode


grunt_build = env.Command(
    target="include/WebPageContent.gen.inc",
    source="Gruntfile.js",
    action=run_grunt_build,
)
env.Depends(grunt_build, npm_ci)
env.Depends(grunt_build, package_json)
env.Depends(grunt_build, env.Glob("webpage/*"))

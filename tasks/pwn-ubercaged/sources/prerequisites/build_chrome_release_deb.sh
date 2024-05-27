cd /home/chrome/chromium/src

# build release
gn gen out/x64.release
cat << EOF > ./out/x64.release/args.gn
target_os = "linux" 
target_cpu = "x64"
enable_nacl = false
is_debug = false
symbol_level = 1
remove_webcore_debug_symbols = true
is_debug = false
enable_linux_installer = true
use_debug_fission = true
dcheck_always_on = false
chrome_pgo_phase = 0
v8_enable_sandbox = true
EOF
gn args out/x64.release

autoninja -C out/x64.release "chrome/installer/linux:unstable_deb"

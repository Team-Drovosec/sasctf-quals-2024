cd /home/chrome/chromium/src

# build debug
gn gen out/x64.debug
cat << EOF > ./out/x64.debug/args.gn
target_os = "linux" 
target_cpu = "x64"
enable_nacl = false
is_debug = false
symbol_level = 2
v8_enable_object_print = true
use_debug_fission = true
dcheck_always_on = false
chrome_pgo_phase = 0
v8_enable_disassembler = true
v8_enable_sandbox = true
EOF
gn args out/x64.debug

autoninja -C out/x64.debug chrome
autoninja -C out/x64.debug d8

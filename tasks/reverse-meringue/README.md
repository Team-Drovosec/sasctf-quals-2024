## Title
Secret meringue recipe

## Description
Whilst our programmer were on a raspberry latte raid to a local coffee shop, intruders installed a sophisticated malware to his laptop. It's unclear what they managed to obtain from this attack so far, but what's clear as sunny day is that our boss will teach the programmer on how to cook marvelous puffed meringue. Seems like he won't ever need a dessert for his coffee again, but what he will surely need is a professional incident response.
We've managed to get a RAM dump from infected machine. We analyzed it using volatility3 and detected some malicious activity inside the process svshost.exe. Unfortunately, our skillset is too poor to figure out the rest.
The boss is on the rage! Can you help us before we get our portion?

## Solution

### Dumping memory of the malicious process
The task description mentions that the process named svshost is malicious. Upon running the `vol.py -f memory.dmp windows.pstree` command it is possible to find out that the PID of this process is `1536`.  Finding the PID makes it possible to dump all the memory regions of the process with the command vol.py -f `C:\Users\User\Downloads\memory_v2.dmp windows.vadinfo.VadInfo --pid 1536 --dump`.

### Analyzing the process executable

One of the largest dumped regions is approximately 85MB in size. It contains the process executable - a .NET file protected with ConfuserEx. All of its functions are flattened (https://reverseengineering.stackexchange.com/questions/2221/what-is-a-control-flow-flattening-obfuscation-technique) -- they have the form demonstrated in the code below.

    public f()
    {
    	for (;;)
    	{
    		IL_06:
    		uint num = 0xE275CFEBU;
    		for (;;)
    		{
    			uint num2;
    			switch ((num2 = (num ^ 0xCC5065F4U)) % 3U)
    			{
    			case 0U:
    				goto IL_06;
    			case 2U:
    				num = (num2 * 0xC4F6AB62U ^ 0xD1F406A7U);
    				continue;
    			}
    			return;
    		}
    	}
    }

The first action performed by the entry point function of the binary creates an object of the `\u200E\u206F\<omitted>` class. Afterwards, the binary crashes.  
Analysis of the `u200E\u206F\<omitted>` class reveals that it contains a method (`\u202E\u200B<omitted>`) responsible for compiling all functions from IL code to assembly and afterwards corrupting the IL code. More precisely, the code searches for expressions of the type `num = (num2 * A ^ B)`, replacing constants `A` and `B` with random numbers. Thus, in order to make the executable working again, it is required to revert the actions of the code that corrupts IL and restore the values of `A` and `B` for each expression described above.  

### Restoring the IL code
The constants `A` and `B` that need to be restored can be extracted from the assembly code found in the address space of the `svshost.exe` process. That can be done with the following steps:

 1. Memory ranges with compiled .NET code inside the `svshost.exe` process are loaded inside IDA with the `load_ranges.py` script, placed in the `writeup` directory.
 2. Functions are defined in IDA by running the `define_functions.py` script.
 3. Flattened functions are found inside among defined functions using the `find_flattened.py` script.
 4. Information about constants is extracted using the 
`extract_constants.py` script.
 Having extracted the constants, it is possible to write a dnlib-based program (`Replacer.cs`) that subsitutes the wrong constants with the correct ones.
 
### Decrypting traffic

After substituting the constants, the binary will become working, making it possible to analyze it dynamically. The binary receives commands from a C2 server, which are then decrypted and executed. To decrypt the payloads in the .pcap file, it is possible to replay the traffic from the C2 server and dynamically decrypt it with the fixed `svshost.exe` binary. The decrypted traffic includes an SQLite database that contains the flag.

## Flag
SAS{l075_0f_fun_w17h_fl4773n1ng}

**Solved by:** 0 teams
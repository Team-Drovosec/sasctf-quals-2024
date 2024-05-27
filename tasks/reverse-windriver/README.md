## Title
Napoleon

## Description
Some crazy guy imagined himself to be Napoleon and attacked our network. Now all the computers in our office crash as soon as we power them on. That freaky guy demanded $10K as ransom to make our computers work again. 
Our IT specialists have looked at the broken computers and found a suspicious driver in it, however, we are too afraid to look at it more closely - the guy told us that he will wipe all the data in our company if we try to remove the infection without his help.
The freak also offered us to remove the infection from one of the machines for free. We managed to capture the process of him interacting with the driver, however, we weren't able to make sense out of these recordings. It seems like there is nothing we can do...

## Solution

### Driver functionality

The first non-library function that gets called inside the driver is `DriverEntry` (located at address`0x140072630`). It performs the following actions:
 1. Creates a device object used for communications with the driver (`\Device\there_is_nothing_you_can_do`);
 2. Initializes a global SHA-256 hash context;
 3. Creates a new thread that sleeps for 5 minutes and then checks if the file `SystemRoot\system32.rds` is present on the machine. If it is not, it crashes the system by derefencing a NULL pointer.

The driver is also able to receive IOCTL requests from userland applications. In total, it is configured to handle 10001 different IOCTL request codes. 10000 of these codes are responsible for updating the global SHA256 hash context with a unique string. Apart from them, there is a request type with the code `2261288`. When it is received, the driver:

 1. Finalizes computation of the SHA256 hash performed via the global context;
 2. Attempts to decrypt a blob stored inside the driver's `.data` section with RC4, using the calculated SHA256 hash value as the key;
 3. If the decryption is successful, creates the file named `SystemRoot\system32.rds`, thus preventing the system from crashing.

Thus, in order for the RC4 decryption to be performed correctly, it is required to issue the 10000 requests that update the SHA256 hash in the correct order. 

### Retrieving the order in which the IOCTL requests need to be called

Among the files provided with the challenge was an archive named `devIOD.sys`. It contains 10001 folders, and the name of each folder is a number - more precisely an IOCTL code handled by the driver.  
The archive also stores the modification time of each folder. Using the modification timestamps, it is possible to restore the sequential order in which the IOCTL requests were issued. To extract the timestamps from the archive, it is possible to use the following command:

    7z l -slt devIOD.7z > output.txt
Afterwards, the following Python script can be used to parse the output of the 7z utility and sort the folders in it by modification time:

    with open(r'output.txt', 'r') as f:
        a = f.read().split("\n\n")
    all_entries = []
    for entry in a:
        if '.data' not in entry and '.conf' not in entry:
            split_entry = entry.split("\n")
            all_entries.append((int(split_entry[0].replace("Path = ", "").replace("devIOD\\", ""), 16), split_entry[3].replace("Modified = ", "")))
    sorted_timestamps = sorted(all_entries, key = lambda x: x[1])

### Decrypting the payload

After figuring out the order in which the requests need to be issued, it is now possible to decrypt the blob inside the driver. To do that, it is possible to launch the driver on a VM with a kernel debugger and place a breakpoint at the RVA `0x71719` of the driver.  After doing that, it is necessary to issue the IOCTLs requests to the driver in the correct order. This can be done with the following C program:

    #include <iostream>
    #include <windows.h>
    
    int main(char argc, char** argv)
    {
        HANDLE device = INVALID_HANDLE_VALUE;
        BOOL status = FALSE;
        DWORD bytesReturned = 0;
        CHAR inBuffer[128] = { 0 };
        CHAR outBuffer[128] = { 0 };
    
    
        device = CreateFileW(L"\\\\.\\there_is_nothing_you_can_do", GENERIC_WRITE | GENERIC_READ | GENERIC_EXECUTE, 0, 0, OPEN_EXISTING, FILE_ATTRIBUTE_SYSTEM, 0);
    
        if (device == INVALID_HANDLE_VALUE)
        {
            printf_s("> Could not open device: 0x%x\n", GetLastError());
            return FALSE;
        }
        int ioctls[] = { /* extracted order */ };    
        int len_ioctls = 10001;
        for (int i = 0; i < len_ioctls; i++) {
            status = DeviceIoControl(device, ioctls[i], inBuffer, sizeof(inBuffer), outBuffer, sizeof(outBuffer), &bytesReturned, (LPOVERLAPPED)NULL);
    
        }
    
        CloseHandle(device); 
        }

After doing that, the previously set breakpoint will trigger, and it will be possible to extract the SHA256 hash value by reading the RC4 key from memory, which is stored at address `rsp+0x108`.  Decrypting the blob inside the driver with the extracted key will yield a JPG file with the flag.

## Flag
SAS{d4n5_m0n_3spr17_70u7_d1v4gu3}

**Solved by:** 4 teams

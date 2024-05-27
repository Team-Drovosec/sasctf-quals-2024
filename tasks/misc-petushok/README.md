## Title
Petushok

## Description
koekeloekoe kykyliky kukeleku cock-a-doodle-doo kukko kiekuu cocorico kikeriki kikiriku kukuriku kukuriku kukareku chicchirichi kokekokko kkokkodek kko wo-wo-wo ghoo-ghoo-lee ghoo-ghoo cucurigu kuk-do-kuk kuk-kurri-kuuu ek-i-ek-ek kuckeliku co-co-co...

## Solution
### Disclaimer
There is a misconfiguration in Dockerfile which lead to opcode_ids.h being copied to "include" instead of "Include". Python built without opcode shuffling and the task became as easy as using pycdc and z3 :(

### Solution

There is web application based on `flask` library. Default page redirects you to
`http://localhost:8080/?logo=petushok`

#### Part 1
Application takes `logo` param and if there is no extension, it tries to guess the extension of the file in current folder. For example:
`petushok => petushok.png`
and
`petushok.png => petushok.png`

Content of the file is read, encoded to base64 and inserted to HTML body.
If you try to pass a folder instead of a file, you will receive debug information inside the HTML page:

```
<!-- DEBUG 
list of available files:
__pycache__
server.pyc
wsgi.pyc
helper.pyc
templates
wsgi.py
server.py
petushok.png
-->
```

To sum up: you can download any file including `server.py`. You can also download `helper.pyc` which is used for validation of the secret.

#### Part 2
Straightforward move would be to decode `helper.pyc` into `helper.py` and get all the logic used to validate the `secret`. This will not work out because it is compiled by `bad python`. The difference between `python` and `bad python` that all opcode values have been shuffled.

To proceed you can download `server.py` and corresponding `server.pyc` then compare it with the proper `server.pyc` to spot the difference. Then you can convert bad `helper.pyc` to good `helper.pyc`, decode it and inverse the operations done on the secret.

There's apparently many solves for the equation, for example z3 outputs `[secret = 3965251753348952990461306387064706394071645273297028234756978954838]` which is also a valid secret.

#### Getting the flag
`http://localhost:8080/?logo=petushok&secret=20378257353180406617201586284835596680265125727239853295990471852018019390038`


## Flag
SAS{kuP1l_muzh1k_p3Tuh4_4_0n_3mu_k4K_r3z}

**Solved by:** 36 teams
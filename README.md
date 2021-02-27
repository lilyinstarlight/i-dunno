# I-DUNNO Implementation

This library implements the Internationalized Deliberately Unreadable Network Notation (shortened as I-DUNNO) as defined in [RFC 8771](https://www.rfc-editor.org/rfc/rfc8771.html). The library supports encoding and decoding I-DUNNO representation, but the command line interface only supports encoding and does not implement decoding, as the RFC recommends the output of such a function SHOULD NOT be presented to humans.

## CLI Usage

    $ pip install i-dunno
    $ i-dunno 198.51.100.164


## API Usage

```python
import ipaddress

import i_dunno


addr = ipaddress.ip_address('198.51.100.164')
addr_i_dunno = i_dunno.encode(addr, level='satisfactory')
addr_obj = i_dunno.decode(addr_i_dunno)
```

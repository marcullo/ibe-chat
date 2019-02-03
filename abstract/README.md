# Abstract

> Diagrams of operations. Simplified.

## Procedure

Originally, the process [should](https://crypto.stanford.edu/~dabo/pubs/papers/bfibe.pdf) implement 4 steps:

1. **Setup** - create IBE environment system parameters (master public key, parameters of encryption, message and ciphertext space). Made by *Private Key Generator*.
2. **Extract** - get private key. Made by *Client*.
3. **Encrypt** - encrypt message using system parameters and Recipient's public key. Made by *Sender*.
4. **Decrypt** - decrypt ciphertext using Recipient's private key. Made by *Recipient*.

The following proof of concept is a little bit different, but the idea was preserved.

**Note**: *Extract* process should be made in an isolated, secure way, preliminarily off-line in the cooperation with system administrator. However this project simplifies the process for getting the private key from *PKG* explicitly.

## Implementation

### Setup

![Setup](operations-setup.png)

*Fig.1. Setup. In this project the Server has a role of Key Authority.*

![Identity exchange](operations-exchange-identiites.png)

*Fig. 2. Identity exchange between parties.*

![Key obtainment](operations-obtain-keys.png)

*Fig.3. Key obtainment.*

![Key generation](operations-generate-keys.png)

*Fig.4. Key generation.*

### Chat

![Message sending](operations-send-message.png)

*Fig.5. Message sending*.

![Message receiving](operations-receive-messages.png)

*Fig.6. Message receiving*.

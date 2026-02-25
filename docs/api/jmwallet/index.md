# jmwallet

Wallet implementation for JoinMarket NG.

## Modules

### Main Modules

| Module | Description |
|--------|-------------|
| [history](history.md) | Transaction history |
| [utxo_selector](utxo_selector.md) | UTXO selection |

### CLI

| Module | Description |
|--------|-------------|
| [bonds](cli/bonds.md) | Bond management CLI |
| [cold_wallet](cli/cold_wallet.md) | Cold wallet CLI |
| [freeze](cli/freeze.md) | Freeze UTXOs CLI |
| [history_cmd](cli/history_cmd.md) | History CLI |
| [mnemonic](cli/mnemonic.md) | Mnemonic utilities CLI |
| [registry](cli/registry.md) | Registry CLI |
| [send](cli/send.md) | Send transactions CLI |
| [wallet](cli/wallet.md) | Wallet management CLI |

### Wallet

| Module | Description |
|--------|-------------|
| [address](wallet/address.md) | Address management |
| [bip32](wallet/bip32.md) | BIP32 HD keys |
| [bond_registry](wallet/bond_registry.md) | Fidelity bond registry |
| [coin_selection](wallet/coin_selection.md) | Coin selection |
| [constants](wallet/constants.md) | Wallet constants |
| [display](wallet/display.md) | Display utilities |
| [models](wallet/models.md) | Wallet models |
| [service](wallet/service.md) | Wallet service |
| [signing](wallet/signing.md) | Transaction signing |
| [sync](wallet/sync.md) | Wallet synchronization |
| [utxo_metadata](wallet/utxo_metadata.md) | UTXO metadata |

### Backends

| Module | Description |
|--------|-------------|
| [base](backends/base.md) | Base backend |
| [bitcoin_core](backends/bitcoin_core.md) | Bitcoin Core backend |
| [descriptor_wallet](backends/descriptor_wallet.md) | Descriptor wallet backend |
| [mempool](backends/mempool.md) | Mempool backend |
| [neutrino](backends/neutrino.md) | Neutrino backend |

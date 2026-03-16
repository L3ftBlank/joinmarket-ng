🚧 **This JoininBox documentation is a Work in Progress** 🚧

# Mainmenu

<span id="top"></span>
<div class="terminal-menu">
┌────────────────JoininBox v0.8.5 mainnet─────────────────┐
│                                                         │
│   Choose from the options:                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │                                                   │  │
│  │<a href="#mm-01">START</a>     Quickstart with JoinMarket               │  │
│  │                                                   │  │
│  │<a href="#mm-02">WALLET</a>    Wallet management options                │  │
│  │<a href="#mm-03">MAKER</a>     Yield Generator options                  │  │
│  │                                                   │  │
│  │<a href="#mm-04">SEND</a>      Pay to an address with/without a coinjoin│  │
│  │<a href="#mm-05">FREEZE</a>    Exercise coin control within a mixdepth  │  │
│  │<a href="#mm-06">PAYJOIN</a>   Send/Receive between JoinMarket wallets  │  │
│  │                                                   │  │
│  │<a href="#mm-07">OFFERS</a>    Watch the Order Book locally             │  │
│  │                                                   │  │
│  │<a href="#mm-08">CONFIG</a>    Connection and joinmarket.cfg settings   │  │
│  │<a href="#mm-09">TOOLS</a>     Extra helper functions and services      │  │
│  │<a href="#mm-10">UPDATE</a>    Update JoininBox or JoinMarket           │  │
│  │                                                   │  │
│  │<a href="#mm-11">BLITZ</a>     Switch to the RaspiBlitz menu            │  │
│  │<a href="#mm-12">REBOOT</a>    Restart the computer                     │  │
│  │<a href="#mm-13">SHUTDOWN</a>  Switch off the computer                  │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│               <a href="#top">< Select ></a>        <a href="#top">< Exit ></a>                │
└─────────────────────────────────────────────────────────┘
</div>
---

## START {#mm-01}

<details>
<summary>Quickstart with JoinMarket</summary>

This section provides a quick entry point into using JoinMarket. It allows you to set up a new wallet, view deposit addresses, start earning fees as a maker, and access the documentation via QR code. All commands here are designed for rapid setup and basic wallet operations.
</details>

<div class="terminal-menu">
┌──────────────Quickstart options─────────────────┐
│ ┌─────────────────────────────────────────────┐ │
│ │<a href="#mt">GEN</a>     Generate a new wallet                │ │
│ │<a href="#ws">M0</a>      Show the first mixdepth to deposit to│ │
│ │<a href="#ws">DISPLAY</a> Show the contents of all mixdepths   │ │
│ │<a href="#ws">MAKER</a>   Run the Yield Generator              │ │
│ │<a href="#mt">DOCS</a>    Link to the documentation            │ │
│ └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│           <a href="#mm-01">< Select ></a>    <a href="#top">< Back ></a>                │
└─────────────────────────────────────────────────┘
</div>

| Option | Explanation |
|--------|---------------------------|
| GEN | **Generate Wallet** - Creates a new JoinMarket wallet from scratch. Unlike standard Bitcoin wallets, a JoinMarket wallet is pre-divided into 5 "mixdepths" (0-4). These act as separate compartments to isolate funds at different privacy levels, which is essential for effective coinjoins. Choose a strong password and store the 12-24 word recovery seed safely offline. |
| M0 | **First Deposit Address** - Displays a receiving address from mixdepth 0. This is the standard entry point for new funds entering your wallet. All funds deposited here are considered "unmixed" until they are involved in a coinjoin or moved to a higher mixdepth. Always use a new address for each deposit for better privacy. |
| DISPLAY | **Show All Addresses** - Lists receiving addresses across all 5 mixdepths (0-4). In JoinMarket, funds in different mixdepths are mathematically isolated from each other on the blockchain. Moving funds from depth 0 to 4 through coinjoins breaks the link between your deposit and your spend, significantly increasing privacy. |
| MAKER | **Start Yield Generator** - ??? Runs the automated maker service. As a Maker, you provide liquidity to the JoinMarket network by offering your coins for coinjoins. Takers pay you a fee (in Satoshis) to participate in their transactions. This earns passive income while preserving your privacy. The more coins you have available across different mixdepths, the more offers you can make.

Runs the automated maker service. As a Maker, you advertise your coins on the JoinMarket network for use in coinjoins. When a Taker selects your offer, your coins are included in the transaction and you earn a fee in Satoshis. Run this as a background service to earn passive income while improving the privacy of the entire network. |
| DOCS | **Documentation QR Code** - ??? Opens a QR code that links to the JoinMarket NG documentation website. Scan with your phone to read setup guides, troubleshooting tips, and advanced features. |

---

## WALLET {#mm-02}

<details>
<summary>Wallet management options</summary>

This section contains all tools to manage your Bitcoin wallet securely. View balances, transaction history, and public keys. Generate new wallets, restore from seed, or import from another node. Use coin control features to freeze specific coins and manage UTXOs efficiently.
</details>

<div class="terminal-menu">
┌────────────Wallet management options─────────────┐
│ ┌──────────────────────────────────────────────┐ │
│ │<a href="#ws">DISPLAY</a>     Show the contents of all mixdepths│ │
│ │<a href="../labels/">LABEL</a>       Add or edit a label to an address │ │
│ │<a href="#ws">UTXOS</a>       Show all the coins in the wallet  │ │
│ │<a href="#ws">HISTORY</a>     Show all past transactions        │ │
│ │<a href="#ws">XPUBS</a>       Show the master public keys       │ │
│ │<a href="#ws">PSBT</a>        Sign a Base64 format PSBT         │ │
│ │<a href="#mt">GEN</a>         Generate a new wallet             │ │
│ │<a href="#mt">IMPORT</a>      Copy wallet(s) from a remote node │ │
│ │<a href="#ws">SHOWSEED</a>    Shows the wallet recovery seed    │ │
│ │<a href="pic">RECOVER</a>     Restore a wallet from the seed    │ │
│ │<a href="#ws">INCREASEGAP</a> Increase the gap limit            │ │
│ │<a href="../rescan/">RESCAN</a>      Rescan the Bitcoin Core wallet    │ │
│ │<a href="../unlock/">UNLOCK</a>      Remove the lockfiles              │ │
│ └──────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────┤     
│            <a href="#mm-02">< Select ></a>      <a href="#top">< Back ></a>              │
└──────────────────────────────────────────────────┘
</div>

| Option | Explanation |
|--------|---------------------------|
| DISPLAY | **Show Wallet Contents** - Displays all mixdepths with their balances and addresses. Mixdepth 0 is the entry point for new, unmixed deposits (lowest privacy). Higher mixdepths (1-4) contain funds that have been processed through coinjoins (higher privacy). Use this to see how your funds are distributed across privacy levels. |
| LABEL | **Add/Edit Label** - Assigns a custom name or note to a specific address. Useful for tracking who sent Bitcoin or what the funds are for. Labels help organize your wallet when addresses become unrecognizable. |
| UTXOS | **Show All Coins** - Displays every Unspent Transaction Output (UTXO) in your wallet. Each UTXO represents a discrete "coin" with a specific history on the blockchain. Understanding your UTXOs is crucial for privacy: spending multiple UTXOs together in one transaction links them publicly. Use this view to select which specific coins to freeze or spend for optimal privacy. |
| HISTORY | **Show Transaction History** - Lists all wallet transactions including deposits, withdrawals, and coinjoins. Shows timestamps, amounts, and transaction IDs. Use this to verify that coinjoin transactions completed successfully or to reconcile your balance records. |
| XPUBS | **Show Master Public Keys** - Displays the extended public keys (xpub/zpub) for each mixdepth. An xpub can generate all receiving addresses for that mixdepth but cannot spend funds. Warning: Sharing an xpub reveals your complete transaction history and balance for that mixdepth to the recipient. Only share with trusted accountants or watch-only wallet services. |
| PSBT | **Sign PSBT** - Signs a Partially Signed Bitcoin Transaction (PSBT) in Base64 format. This enables offline signing workflows: create a transaction on an online "watch-only" computer, transfer the PSBT (via USB/QR) to this JoinMarket machine, sign it, and return it for broadcast. Essential for air-gapped security setups or integrating with hardware wallets. |
| GEN | **Generate New Wallet** - Creates a new JoinMarket wallet from scratch. Unlike standard Bitcoin wallets, a JoinMarket wallet is pre-divided into 5 "mixdepths" (0-4). These act as separate compartments to isolate funds at different privacy levels, which is essential for effective coinjoins. Choose a strong password and store the 12-24 word recovery seed safely offline. |
| IMPORT | **Import from Remote Node** -  Securely copies wallet files (wallet.jmdat) from a remote server using SSH/SCP. Useful for migrating a wallet to a new machine or restoring from a backup server. Ensure the remote node is trusted and the connection is secure (Tor/SSH) to protect sensitive wallet data during transfer. |
| SHOWSEED | **Show Recovery Seed** - Displays your 12-24 word seed phrase. **NEVER share this with anyone!** This seed allows you to restore your wallet if you lose access. Write it down and store it safely. |
| RECOVER | **Restore from Seed** - Recreates your wallet from a 12-24 word mnemonic seed phrase. This recovers all funds and mixdepth addresses derived from that seed. Note: Custom labels and fidelity bond timelock addresses are not restored from the seed alone. Ensure you have a verified backup of your seed before proceeding. |
| INCREASEGAP | **Increase Gap Limit** - Sets how many unused addresses the wallet scans forward for transactions. The default is 20. Increase this value if you restored a wallet and notice missing funds (e.g., if you previously used addresses beyond the default gap). A higher gap limit slows down wallet scanning but ensures all historical addresses are found. |
| RESCAN | **Rescan Blockchain** - Triggers a blockchain rescan starting from a specific block height (or genesis block). This forces the node to re-examine all blocks for transactions involving your wallet addresses. Use this if transactions are missing after a restore that you know are confirmed on-chain, but avoid unnecessary full rescans as they are time-consuming. |
| UNLOCK | **Remove Lock Files** - ??? Deletes wallet lock files (`.lock` files) that may be stuck from a previous crash. **Only do this when Bitcoin Core is not running!** This may cause data corruption if wallet is open. |

---

## MAKER {#mm-03}

<details>
<summary>Yield Generator options</summary>

The Yield Generator (YM) is JoinMarket's automated trading service that provides liquidity to the network in exchange for fees. It matches your orders with takers for coinjoins and earns Satoshis as compensation. Configure settings, monitor earnings, and control the service here.
</details>

<div class="terminal-menu">
┌────────────Yield Generator options──────────────┐
│ ┌─────────────────────────────────────────────┐ │
│ │<a href="../maker/">MAKER</a>    Run the Yield Generator             │ │  
│ │<a href="../jmconf/">JMCONF</a>   YG settings in the joinmarket.cfg   │ │ 
│ │<a href="../yglist/">YGLIST</a>   List the past YG activity           │ │ 
│ │<a href="../stats/">STATS</a>    Show the sats earned as a Maker     │ │
│ │<a href="../nickname/">NICKNAME</a> Show the last used counterparty name│ │
│ │<a href="../service/">SERVICE</a>  Monitor the YG service (INFO)       │ │
│ │<a href="../logs/">LOGS</a>     View the last YG logfile (DEBUG)    │ │
│ │<a href="../stop/">STOP</a>     Stop the YG service                 │ │
│ │<a href="../timelock/">TIMELOCK</a> Create a Fidelity Bond address      │ │
│ └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│          <a href="#mm-03">< Select ></a>     <a href="#top">< Back ></a>                │
└─────────────────────────────────────────────────┘
</div>

| Option | Explanation |
|--------|---------------------------|
| MAKER | **Start Yield Generator** - ??? Runs the automated maker service. As a Maker, you provide liquidity to the JoinMarket network by offering your coins for coinjoins. Takers pay you a fee (in Satoshis) to participate in their transactions. This earns passive income while preserving your privacy. The more coins you have available across different mixdepths, the more offers you can make. **Start Yield Generator** ??? Runs the automated maker service. As a Maker, you advertise your coins on the JoinMarket network for use in coinjoins. When a Taker selects your offer, your coins are included in the transaction and you earn a fee in Satoshis. Run this as a background service to earn passive income while improving the privacy of the entire network. |
| JMCONF | **Edit Yield Generator Config** - Opens the joinmarket.cfg file to manually edit settings, e.g. for makers and takers. Here you can configure minimum offer amounts, relative fees, and the minimum coinjoin size you accept. Warning: Editing this file manually requires understanding of JoinMarket parameters. Incorrect values may prevent you from earning or accepting offers. |
| YGLIST | **Yield Generator History** - Shows a CSV log of past Yield Generator activity. Includes timestamps, counterparty names, and earnings. Review this to track your income history and network activity over time. |
| STATS | **Maker Earnings Stats** - Displays total Satoshis earned as a Maker from coinjoin fees. Shows a summary of completed coinjoins and total profit. |
| NICKNAME | **Show Last Counterparty Nickname** - Displays the Nickname (pseudonymous identifier) of the last Taker you matched with in a coinjoin. This helps track counterparties over time. Note: Nicknames are generated deterministically from public keys and rotate periodically, so they are not permanent identities. |
| SERVICE | **Service Status Monitor** - Checks if the Yield Generator service is running as a systemd service. Shows active/inactive status and uptime. Useful for troubleshooting why the service isn't working. |
| LOGS | **View Debug Logs** - Displays the Yield Generator's log output (typically at DEBUG level). Shows detailed information about offer broadcasts, transaction negotiations, and errors. Caution: Logs may contain sensitive information about your transactions; avoid sharing them publicly without redaction. |
| STOP | **Stop Yield Generator** - Gracefully stops the Yield Generator service. Use when you want to pause earning or troubleshoot issues. Can be restarted later without losing configuration settings. |
| TIMELOCK | **Create Fidelity Bond** - ??? Generates a special address to lock bitcoins for a fixed period (e.g., 6 months). This creates a cryptographic proof that you are a legitimate market maker, not a Sybil attacker trying to spy on the network. Bonds are displayed in the Order Book, increasing your reputation and allowing you to earn higher fees from Takers. Your locked funds cannot be spent until the time lock expires. |

---

## SEND {#mm-04}

<details>
<summary>Pay to an address with or without a coinjoin</summary>

Send Bitcoin from your wallet to any recipient. Configure privacy settings by adjusting maker count, transaction fees, and mix depths. Send with coinjoins for enhanced privacy. All parameters are set interactively before sending.
</details>

<div class="terminal-menu">
┌────────────────────Confirm the details───────────────────────────┐
│                                                                  │
│ From the wallet: jmw.jmdat                                       │
│ mixdepth: 0                                                      │
│ send: 100000 sats                                                │
│ coinjoin: with 5 makers                                          │
│ miner fee: 2 sat/byte                                            │
│ destination address:                                             │
│ bc1qar0sabc7xfkvy5l643lydnw9re59gtzzwf5mdq                       │
│ change address (optional):                                       │
│ internal address in m0                                           │
│                                                                  │
│                       [ Yes ]    [ No ]                          │
└──────────────────────────────────────────────────────────────────┘
</div>

| Parameter | Explanation |
|-----------|---------------------------|
| mixdepth | **Choose Send From** - Select the mixdepth (0-4) to fund the transaction from. Mixdepth 0 is typically where new, unmixed deposits arrive (lowest privacy). Higher mixdepths (1-4) usually contain funds that have been processed through coinjoins (higher privacy). Spending from higher mixdepths provides better anonymity for the recipient. Choose the depth that matches the privacy level you wish to send. |
| amount | **Enter Amount in Satoshis** - Specify how much Bitcoin to send in satoshis (1 BTC = 100,000,000 sats). Enter 0 to send entire mix depth balance. Double-check the amount before confirming. |
| makercount | **Coinjoin Participation** - ??? Select the number of other liquidity providers (Makers) to include in your transaction. A higher count (e.g., 7-9) creates a larger anonymity set, making the transaction harder to trace. However, this increases the total coinjoin fees paid (each Maker charges a small fee). Setting this to 0 sends a standard transaction without coinjoin, which is cheaper but offers no privacy enhancement. |
| txfee | **Miner Fee in Sat/Byte** - Set the transaction fee paid to miners for confirmation. Higher fees = faster confirmation. From the config, typical values are 3 sat/byte (or ~3000 sats total). This is separate from coinjoin fees paid to Makers. |
| address | **Recipient Bitcoin Address** - Enter the destination Bitcoin address for the transaction. Verify the address carefully before sending to avoid lost funds. Supports mainnet addresses (bc1, 1, or 3 prefix). |
| changeAddress | **Optional Change Address** - Provide a custom address for any leftover change (if sending partial amount). If empty, change goes back to wallet automatically. Useful for batch processing to multiple addresses. |

---

## FREEZE {#mm-05}

<details>
<summary>Exercise coin control within a mixdepth</summary>

Allows you to freeze specific UTXOs in a selected mixdepth so they won't be automatically selected for spending. This is useful for privacy planning: prevent certain coins from being linked together in a single transaction. Frozen coins show as "frozen" in the UTXO list.

</details>

| Parameter | Explanation |
|-----------|---------------------------|
| mixdepth | **Choose Mix Depth** - Select which mix depth (0-4) to freeze coins in. Each mix depth has its own set of coins. Freeze only coins in specific privacy levels while leaving others available for sending. |

---

## PAYJOIN {#mm-06}

<details>
<summary>Send/Receive between JoinMarket wallets</summary>

PayJoin is a privacy technology where the receiver contributes coins to the transaction, making it look like a regular payment rather than a coinjoin. Send payments or receive funds with enhanced privacy through this protocol. Both parties need PayJoin supporting wallets.
</details>

| Option | Explanation |
|--------|---------------------------|
| SEND | **Send with PayJoin** - Initiates a BIP78 PayJoin transaction to another JoinMarket wallet. Unlike standard coinjoins, the receiver contributes inputs to the transaction, making it appear as a simple transfer to blockchain observers. This defeats the "common input heuristic" used by chain analysts, significantly improving privacy for both sender and receiver. The recipient wallet must support PayJoin. |
| RECEIVE | **Receive with PayJoin** - Starts a listener service to accept incoming BIP78 PayJoin transactions. Your wallet will automatically contribute inputs to the transaction when someone pays you, mixing your coins during the receive process. Note: Requires your wallet to be unlocked and the service running at the time of payment. |

---

## OFFERS {#mm-07}

<details>
<summary>Watch the Order Book locally</summary>

Displays the peer-to-peer marketplace where Makers publish their available coinjoin offers. There is no central server; this data is gathered from the IRC network channels. Use this to analyze the market: check current fee rates, available liquidity sizes, and the total number of active Makers. Monitoring the Order Book helps you decide when to run a Taker or Maker operation.
</details>

| Option | Explanation |
|--------|---------------------------|
| START | **Start Order Book Watch** - Launches a read-only observer for the JoinMarket P2P marketplace. Connects to IRC channels to aggregate offers from Makers. This is for monitoring only; running this does not make you a Maker or Taker. Useful for analyzing market conditions before running a Yield Generator. |
| SHOW | **Show Order Book Address** - Displays your local Order Book .onion address for the Tor network. Others can connect to your node to see what you're offering or trading with. Share carefully as it exposes your node. |
| STOP | **Stop Background Process** - Terminates the Order Book watcher service. Use when you no longer need to monitor offers or to free up system resources. Can be restarted anytime without configuration loss. |

---

## CONFIG {#mm-08}

<details>
<summary>Connection and joinmarket.cfg settings</summary>

Configure all connection settings for Bitcoin Core and JoinMarket. Connect to local or remote Bitcoin nodes, edit configuration files, or switch network modes. These settings determine how your wallet communicates with the blockchain and network.
</details>

| Option | Explanation |
|--------|---------------------------|
| JMCONF | **Edit JoinMarket Config** - Opens the main JoinMarket configuration file for manual editing. Customize wallet paths, network settings, and protocol options. Changes require restarting services to take effect. |
| CONNECT | **Connect Remote Node** - Configures JoinMarket to use a remote Bitcoin Core node instead of a local one. Enter the RPC credentials (user/password) and network address (IP or .onion). Tip: Using a Tor .onion address is highly recommended to protect your IP address and connection metadata from network observers. |
| SIGNET | **Switch to Signet Network** - Reconfigures JoinMarket to operate on the Signet test network. Signet is a stable test network with reliable blocks, ideal for learning and testing coinjoins without risk. Note: Requires a running Bitcoin Core node with signet=1 configured. |
| LOCAL | **Connect Local Bitcoin Core** - Connects to the Bitcoin Core node running on the same computer. Uses local file paths and default ports (8332). Fastest connection with lowest latency. |
| BTCCONF | **Edit Bitcoin Config** - Opens the Bitcoin Core configuration file (bitcoin.conf) for advanced configuration. Modify RPC settings, pruning options, connection rules, and more. Warning: Incorrect settings can prevent Bitcoin Core from starting. Always make a backup before editing and verify syntax carefully.|
| RESET | **Reset JoinMarket Config** - Deletes and recreates the joinmarket.cfg file with default values. Use this if your configuration is broken or corrupted. You'll need to re-enter all custom settings afterward. |

---

## TOOLS {#mm-09}

<details>
<summary>Extra helper functions and services</summary>

This section contains utility tools and services that support the main JoinMarket functionality. Generate QR codes, run custom RPC commands, scan for coinjoins, or manage system services. Use these tools for maintenance, debugging, and advanced operations.
</details>

| Option | Explanation |
|--------|---------------------------|
| QR | **Generate QR Code** - Displays text or data as a scannable QR code in the terminal. Useful for quickly transferring addresses, xpubs, or connection URIs to a mobile wallet. Note: QR codes are simply visual representations and do not encrypt the data; do not scan sensitive seed phrases with devices you don't trust. |
| CUSTOMRPC | **Run Custom RPC Command** - Execute any Bitcoin Core RPC command using curl. Advanced users can query blockchain data directly. Useful for debugging and advanced blockchain analysis. |
| CJFINDER | **Find Coinjoin Transactions** - Scans the blockchain to identify transactions that match the typical JoinMarket coinjoin pattern (equal-sized outputs). Lists detected coinjoins with addresses and amounts. Useful for research and network analysis. |
| CHECKTXN | **Transaction Explorer** -  Queries your local Bitcoin Core node for transaction details without relying on external block explorers. Enter a txid to view inputs, outputs, amounts, and confirmation status. Using a local explorer preserves privacy by avoiding third-party websites that could log your queries. |
| PASSWORD | **Change SSH Password** - Changes your system SSH login password. Use this to improve account security on the RaspiBlitz system. Choose a strong, memorable password for account protection. |
| SSH | **Enable SSH Access** - Turns SSH access on or off for the joinmarket user. Enable this to access the system remotely via SSH client. Disable for improved security if remote access is not needed. |
| LOGS | **View Bitcoin Core Logs** - Displays the latest bitcoind log files on mainnet. Shows blockchain sync status, peer connections, and any errors. Essential for troubleshooting node issues. |
| API | **Start Wallet API Service** - ??? Launches jmwalletd.py as a systemd service for API access. Required for third-party wallet integrations and external tools. Runs automatically with system startup. |
| FULLYNODED | **Connect Fully Noded** - ??? Provides a QR code to connect Fully Noded hardware wallet. Scan with your Noded device to establish secure connection. Used for high-security cold wallet integration. |

---

## UPDATE {#mm-10}

<details>
<summary>Update JoininBox or JoinMarket</summary>

Keep your JoinMarket installation up to date with the latest security patches and features. Update the JoininBox scripts themselves, the JoinMarket software, or access advanced options like testing pull requests and custom versions.
</details>

| Option | Explanation |
|--------|---------------------------|
| JOININBOX | **Update JoininBox Scripts** - Pulls the latest changes from the JoininBox GitHub repository. This updates the menu system, helper scripts, and documentation, but does not update the underlying JoinMarket software. Run this to get new features, bug fixes, and documentation updates for the menu interface. |
| JOINMARKET | **Update JoinMarket Software** - Fetches and installs the latest stable release of the JoinMarket clientserver software from the official repository. This updates the core coinjoin engine, wallet logic, and protocol support. Note: You may need to restart your Yield Generator or unlock your wallet after this update. |
| ADVANCED | **Advanced Update Options** - Opens menu with deeper update controls. Test new features, install custom versions, or update Tor. Use with caution and only if you understand the implications. |

### Advanced Update Options {#mm-10-1}

| Option | Explanation |
|--------|---------------------------|
| JBCOMMIT | **Update JoininBox Commit** - Updates JoininBox to the latest git commit hash. Includes pre-release features that haven't been officially released yet. May contain bugs. |
| JBPR | **Test JoininBox Pull Request** - Tests a specific Pull Request on JoininBox. Use this to preview upcoming features before official release. Not recommended for production use. |
| JBRESET | **Reset JoininBox Installation** - Completely reinstalls JoininBox scripts from scratch. Use if the installation is corrupted or you want a fresh start. All settings will be reset to defaults. |
| JMCUSTOM | **Update JoinMarket Custom Version** - Install a custom or modified version of JoinMarket. Use this for development, testing, or specialized builds. Not the official release version. |
| JMPR | **Test JoinMarket Pull Request** - Tests a specific Pull Request on JoinMarket software. Preview upcoming JoinMarket features and improvements. Use for development or evaluation purposes only. |
| JMCOMMIT | **Update JoinMarket Commit** - Updates JoinMarket to the latest git commit hash. Contains the newest code from the repository. May be unstable if features are not fully tested. |
| TOR | **Update Tor to Alpha** - Updates the Tor proxy to the latest alpha version. Latest Tor versions offer better privacy and censorship resistance. Alpha versions may have bugs. |

---

## BLITZ {#mm-11}

<details>
<summary>Switch to the RaspiBlitz menu</summary>

Switches from JoininBox menu to the RaspiBlitz administration menu. This is only available when using JoininBox on a RaspiBlitz Bitcoin node. Provides full control over your RaspiBlitz system and services.
</details>

| Option | Explanation |
|--------|---------------------------|
| BLITZ | **Switch to RaspiBlitz Menu** - Exits JoininBox and switches to the RaspiBlitz administration interface. Use this to configure your RaspiBlitz node, check system status, or access advanced features. |

---

## REBOOT {#mm-12}

<details>
<summary>Restart Computer</summary>

Reboots the entire system. Use this to apply system updates, restart stuck services, or clear temporary issues. The Yield Generator will be stopped gracefully before reboot. After restart, you may need to manually restart services like Bitcoin Core or the Yield Generator.
</details>

| Option | Explanation |
|--------|---------------------------|
| REBOOT | **Restart Computer** - Reboots the entire system. Use this to apply system updates, restart stuck services, or clear temporary issues. The Yield Generator will be stopped gracefully before reboot. After restart, you may need to manually restart services like Bitcoin Core or the Yield Generator. |

---

## SHUTDOWN {#mm-13}

<details>
<summary>Shutdown Computer</summary>

Safely powers off the system. Always use this instead of unplugging power to prevent data corruption. The system will gracefully stop the Yield Generator and Bitcoin Core before cutting power. Wait for the "Power down" message or lights to turn off before disconnecting power.
</details>

| Option | Explanation |
|--------|---------------------------|
| SHUTDOWN | **Shutdown Computer** - Safely powers off the system. Always use this instead of unplugging power to prevent data corruption. The system will gracefully stop the Yield Generator and Bitcoin Core before cutting power. Wait for the "Power down" message or lights to turn off before disconnecting power. |
---

<a id="ws"></a>
Input Menu Wallet Selection

<div class="terminal-menu">
┌──Choose a wallet by typing the full name of the file──┐
│ Directories                  Files                    │
│ ┌─────────────────────────┐┌────────────────────────┐ │
│ │.                        ││ jmw.jmdat              │ │
│ │..                       ││ wXFB.jmdat             │ │
│ │                         ││                        │ │
│ │                         ││                        │ │
│ │                         ││                        │ │
│ │                         ││                        │ │
│ │                         ││                        │ │
│ │                         ││                        │ │
│ │                         ││                        │ │
│ │                         ││                        │ │
│ │                         ││                        │ │
│ │                         ││                        │ │
│ │                         ││                        │ │
│ │                         ││                        │ │
│ └─────────────────────────┘└────────────────────────┘ │
│ ┌───────────────────────────────────────────────────┐ │
│ │/home/joinmarket/.joinmarket/wallets/              │ │
│ └───────────────────────────────────────────────────┘ │
├───────────────────────────────────────────────────────┤
│               < OK  >        <a href="#top">< CANCEL ></a>               │
└───────────────────────────────────────────────────────┘
</div>

---

<a id="mt"></a>
An explanatory text will appear here soon.

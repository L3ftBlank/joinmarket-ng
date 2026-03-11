# Tooltip Test Page

This page demonstrates different types of tooltips in MkDocs Material.

## 1. Link Tooltips

### Inline Link with Tooltip
[JoinMarket-NG](https://github.com/joinmarket-ng/joinmarket-ng "JoinMarket-NG is a privacy-focused Bitcoin implementation that uses CoinJoin transactions")

### Reference-style Link with Tooltip
[GitHub]: https://github.com "GitHub is a development platform inspired by the way you work."

Check out the [JoinMarket-NG] repository on [GitHub].

## 2. Icon Tooltips

### Material Design Icons with Tooltips
:material-lock-outline:{ title="Enhanced privacy feature" } Privacy
:material-security:{ title="Security feature" } Security
:material-shield-check-outline:{ title="Verification mechanism" } Verification

### Icons with Links and Tooltips
[:material-github: GitHub](https://github.com "GitHub platform")
[:material-gitlab: GitLab](https://gitlab.com "GitLab platform")

## 3. Abbreviation Tooltips

*[JM]: JoinMarket
*[NG]: Next Generation
*[CoinJoin]: Bitcoin privacy method that breaks transaction links
*[Taker]: Transaction initiator in JoinMarket
*[Maker]: Liquidity provider in JoinMarket

JM-NG uses CoinJoin transactions where a Taker initiates transactions and Makers provide liquidity.

## 4. Text with Tooltips

### Span Element with Tooltip
<span title="This is a custom tooltip for any text">Hover over this text to see a tooltip</span>

### Code with Tooltip
<code title="This is a Python code snippet">print("Hello, JoinMarket-NG!")</code>

## 5. Image with Tooltip
![JoinMarket Logo](media/logo.svg "JoinMarket-NG Logo - Privacy for Bitcoin")

## 6. Complex Examples

### Combined Icon and Text
:material-information-outline:{ title="Important information" } This is important information about JoinMarket-NG.

### Link with Icon and Tooltip
[:material-book: Documentation](technical/index.md "Technical documentation for JoinMarket-NG")

### Table with Tooltips
| Feature | Description |
|---------|-------------|
| :material-lock-outline:{ title="Privacy feature" } Privacy | Enhanced transaction privacy |
| :material-speedometer:{ title="Performance feature" } Speed | Fast transaction processing |
| :material-shield-check-outline:{ title="Security feature" } Security | Robust security measures |

## 7. Testing Different Tooltip Content

### Short Tooltip
[Short](# "Short")

### Medium Tooltip
[Medium](# "This is a medium-length tooltip with more information")

### Long Tooltip
[Long](# "This is a very long tooltip that contains a lot of information and should wrap properly when displayed to the user")

### Tooltip with Special Characters
[Special](# "Special characters: !@#$%^&*()_+-=[]{}|;':\",./<>?")

### Tooltip with Line Breaks (HTML)
[Line Breaks](# "Line 1<br>Line 2<br>Line 3")

### Tooltip with Formatting (HTML)
[Formatted](# "This is <b>bold</b>, <i>italic</i>, and <u>underlined</u> text")
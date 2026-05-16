# Security & Privacy Notes

This document outlines security and privacy considerations for RayFlow.

## Security Checklist

- [ ] All dependencies are regularly scanned for vulnerabilities.
- [ ] No secrets or credentials are hardcoded in source code.
- [ ] Environment variables are used for any sensitive configuration.
- [ ] Network communication is limited to localhost by default.
- [ ] Art-Net/sACN traffic is not broadcast to public networks.

## Network Safety

### Art-Net and sACN

Art-Net and sACN transmit DMX data over UDP without encryption. This is fine for local development but requires care:

- **Local only:** By default, RayFlow communicates with grandMA3 onPC on localhost (127.0.0.1).
- **No public broadcast:** Never send Art-Net to a public or shared network. Rogue DMX signals could interfere with other lighting systems.
- **Firewall:** Ensure your firewall blocks incoming Art-Net/sACN from external networks.
- **Universe isolation:** Use specific universe numbers to avoid conflicts with other devices on the network.

### OSC Communication

OSC commands to grandMA3 onPC are sent as plain text over UDP:

- **Local only:** OSC should only target localhost or known local IPs.
- **No authentication:** OSC has no built-in authentication. Anyone on the network can send commands.
- **Dry-run by default:** RayFlow console CLI commands print what would be sent unless `--execute` is passed.
- **Command validation:** RayFlow rejects empty OSC commands before sending to prevent accidental console changes.

## Privacy

RayFlow is a personal practice tool. Privacy considerations:

- **No user data:** RayFlow does not collect or transmit personal data.
- **Local storage:** All fixture files, show configs, and session logs are stored locally.
- **No cloud services:** RayFlow does not connect to external cloud services.
- **GDTF downloads:** Fixture files are downloaded from gdtf-share.com (public, open standard).

## Threat Modeling

### Main Threats

| Threat | Likelihood | Impact | Mitigation |
|--------|-----------|--------|------------|
| Rogue Art-Net on shared network | Low | Medium | Localhost-only by default, firewall rules |
| Malicious GDTF file | Low | Low | Validate XML before parsing, use trusted sources |
| OSC command injection | Low | Medium | Validate commands, local-only communication |
| Dependency vulnerability | Medium | Low | Regular dependency scanning, pin versions |

## Incident Response

If a security issue is discovered:

1. **Stop:** Halt all network communication (stop grandMA3 onPC, stop RayFlow bridge).
2. **Assess:** Determine the scope and impact of the issue.
3. **Fix:** Apply the necessary fix (update dependency, patch code, change configuration).
4. **Document:** Record the incident in the session log and update this document.
5. **Verify:** Test that the fix resolves the issue without introducing new problems.

# Network Essentials - Complete Study Notes

## Lecture 1 – Introduction
Topics: Computer networks, course objectives, network elements, nodes, links, network types, Internet vs internet, network performance (throughput, latency, reliability, QoS), switching (circuit vs packet), multiplexing (TDM/FDM/statistical), network design principles and terminology.

### Key concepts:
*   Computer networks connect devices to share resources and information.
*   Packet switching is used by the Internet.
*   Circuit switching reserves a dedicated path.
*   Throughput measures data rate; latency measures delay.
*   Multiplexing allows multiple users to share one communication channel.

## Lecture 2 – Protocols and Models
Topics: Protocols, syntax, semantics, timing, protocol stack, layering, encapsulation, decapsulation, headers, trailers, PDUs, OSI and TCP/IP models.

### Key concepts:
*   Protocols define communication rules.
*   Encapsulation adds headers at each layer.
*   PDUs: Data → Segment → Packet → Frame → Bits.
*   Layering simplifies troubleshooting and interoperability.

## Lecture 3 – OSI Reference Model
Topics: Seven OSI layers, responsibilities, devices, addresses, TCP/UDP, IP, MAC, encapsulation, troubleshooting.

### OSI Layers:
7.  Application
6.  Presentation
5.  Session
4.  Transport
3.  Network
2.  Data Link
1.  Physical

### Remember devices:
*   Router → Layer 3
*   Switch → Layer 2
*   Hub/Repeater → Layer 1

## Lecture 4 – Application Layer

### Protocols:
HTTP(80), HTTPS(443), FTP(20/21), DNS(53), DHCP(67/68), SMTP(25), POP3(110), IMAP(143), SSH(22), Telnet(23), SNMP(161).

Topics: Client-server, P2P, DNS, DHCP, email protocols, secure communication.

## Lecture 5 – Network Layer
Topics: IPv4, IPv6, routing, routers, routing tables, NAT, ICMP, default gateway, public/private IPs, routing protocols (RIP, OSPF, BGP).

### Key concepts:
*   IP provides logical addressing.
*   Routers forward packets.
*   NAT allows multiple private devices to share one public IP.

## Lecture 6 – Transport Layer
Topics: TCP vs UDP, segmentation, reassembly, ports, sockets, TCP three-way handshake, ACKs, retransmission, sliding window, flow control, congestion control.
*   TCP = Reliable
*   UDP = Fast

## Lecture 7 – Data Link Layer
Topics: Ethernet, MAC addresses, framing, switches, ARP, VLANs, CRC, CSMA/CD, CSMA/CA.

### Key concepts:
*   PDU = Frame.
*   Switches use MAC tables.
*   ARP resolves IP → MAC.
*   CRC detects transmission errors.

## Lecture 8 – Network Security
Topics: CIA triad, malware, phishing, social engineering, firewalls, IDS/IPS, VPN, encryption, hashing, MFA, DoS/DDoS, MITM, ARP spoofing.

### CIA:
*   Confidentiality
*   Integrity
*   Availability

## Lecture 9 – Physical Layer
Topics: Transmission media, UTP/STP, fiber optics, Wi-Fi, Bluetooth, bandwidth, throughput, latency, attenuation, repeaters, hubs, topologies.

### Remember:
*   PDU = Bits
*   Fiber = Long distance, high speed
*   Star topology = Most common

## Final Revision

### Most Important Exam Areas:
*   OSI layers and responsibilities
*   TCP vs UDP
*   IPv4 vs IPv6
*   MAC vs IP address
*   Router vs Switch vs Hub
*   Packet vs Frame vs Segment
*   DNS, DHCP, HTTP, HTTPS
*   Three-way handshake
*   ARP process
*   Ethernet frame
*   CIA Triad
*   Firewalls, VPN, IDS/IPS
*   Transmission media and topologies

### Recommended Practice:
1.  Draw the OSI model from memory.
2.  Memorize common port numbers.
3.  Explain packet flow from browser to server.
4.  Solve scenario-based troubleshooting questions.
5.  Compare networking devices and protocols.
import socket
import struct
import time
import sys

NTP_PORT = 123
NTP_TIMESTAMP_DELTA = 2208988800  # Adjust from NTP epoch (1900) to Unix epoch (1970)

def ntp_client(ntp_server):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(5)  # 5-second timeout

    # Construct the NTP request packet (Mode 3 - Client)
    request = struct.pack(
        "!B B B b 3I 8I",
        0b00100011,  # Leap Indicator (0), Version (4), Mode (3 - Client)
        0,  # Stratum (not used by client)
        0,  # Poll Interval
        -6,  # Precision (-6 ≈ 15.6ms)
        0, 0, 0,  # Root Delay, Root Dispersion, Reference ID
        0, 0,  # Reference Timestamp (seconds, fraction)
        0, 0,  # Originate Timestamp (seconds, fraction)
        0, 0,  # Receive Timestamp (seconds, fraction)
        0, 0   # Transmit Timestamp (seconds, fraction)
    )

    orig_timestamp = time.time()  # Client's request send time
    client.sendto(request, (ntp_server, NTP_PORT))

    try:
        data, _ = client.recvfrom(48)  # Receive 48-byte response
        dest_timestamp = time.time()  # Time at which response arrived

        # Unpack response correctly (Extract Transmit Timestamp)
        unpacked = struct.unpack("!12I", data)
        trans_seconds = unpacked[10]  # Transmit Timestamp (Seconds)
        trans_fraction = unpacked[11]  # Transmit Timestamp (Fraction)

        # Convert to Unix time
        trans_timestamp = trans_seconds - NTP_TIMESTAMP_DELTA + (trans_fraction / (2**32))

        # Calculate offset & delay
        offset = ((trans_timestamp - orig_timestamp) + (trans_timestamp - dest_timestamp)) / 2
        delay = (dest_timestamp - orig_timestamp) - (trans_timestamp - orig_timestamp)

        # Print results
        print(f"Offset: {offset:.6f} seconds")
        print(f"Round-trip delay: {delay:.6f} seconds")
        print(f"Updated time: {time.ctime(time.time() + offset)}")

    except socket.timeout:
        print("No response from NTP server.")

   
ntp_client(sys.argv[1])

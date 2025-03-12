import socket
import struct
import time
import sys
import hmac
import hashlib

NTP_PORT = 123
NTP_TIMESTAMP_DELTA = 2208988800  # Adjust from NTP epoch (1900) to Unix epoch (1970)
SECRET_KEY = b"super_secret_key"  # Shared secret between client and server

def generate_hmac(data):
    return hmac.new(SECRET_KEY, data, hashlib.sha256).digest()

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

    # Compute and append HMAC signature
    signature = generate_hmac(request)
    request_with_hmac = request + signature
    print(f"Sent packet length: {len(request) + 32}")  # Should be 80 bytes


    client.sendto(request_with_hmac, (ntp_server, NTP_PORT))

    try:
        data, _ = client.recvfrom(64)  # Expecting 48-byte response + HMAC
        dest_timestamp = time.time()  # Time at which response arrived

        # Separate response and HMAC
        response, received_hmac = data[:48], data[48:]

        # Verify HMAC
        expected_hmac = generate_hmac(response)
        if received_hmac != expected_hmac[:16]:
            print("HMAC verification failed! Possible tampering.")
            return

        # Unpack response (Extract Transmit Timestamp)
        unpacked = struct.unpack("!12I", response)
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ntp_client.py <ntp_server_ip>")
    else:
        ntp_client(sys.argv[1])

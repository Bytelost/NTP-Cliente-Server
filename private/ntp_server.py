import socket
import struct
import time
import hmac
import hashlib

NTP_PORT = 123
NTP_TIMESTAMP_DELTA = 2208988800  # Unix (1970) to NTP (1900)
SECRET_KEY = b"super_secret_key"  # Shared secret between client and server

def generate_hmac(data):
    return hmac.new(SECRET_KEY, data, hashlib.sha256).digest()

def ntp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("0.0.0.0", NTP_PORT))  # Listen on all interfaces

    print(f"NTP Server listening on port {NTP_PORT}")

    while True:
        data, addr = server.recvfrom(64)  # Expecting 48-byte request + HMAC

        # Separate request and HMAC
        request, received_hmac = data[:48], data[48:]


        # Verify HMAC
        expected_hmac = generate_hmac(request)

        if received_hmac != expected_hmac[:16]:
            print(f"Invalid HMAC from {addr}. Dropping packet.")
            continue  # Ignore this packet

        recv_timestamp = time.time() + NTP_TIMESTAMP_DELTA  # Time of reception (NTP format)

        # Extract client's Originate Timestamp
        unpacked = struct.unpack("!12I", request)
        orig_seconds = unpacked[10]
        orig_fraction = unpacked[11]
        orig_timestamp = orig_seconds + orig_fraction / (2**32)

        # Generate Transmit Timestamp (server's current time)
        trans_timestamp = time.time() + NTP_TIMESTAMP_DELTA

        # Construct NTP response (Mode 4 - Server)
        response = struct.pack(
            "!B B B b 11I",
            0b00100100,  # Leap Indicator (0), Version (4), Mode (4 - Server)
            1,  # Stratum (1 - Primary)
            0,  # Poll Interval
            -6,  # Precision (-6 ≈ 15.6ms)
            0,  # Root Delay
            0,  # Root Dispersion
            0x4C4F434C,  # Reference ID (could be server's IP)
            int(trans_timestamp), int((trans_timestamp % 1) * (2**32)),  # Reference Timestamp
            int(orig_timestamp), int((orig_timestamp % 1) * (2**32)),  # Originate Timestamp (client)
            int(recv_timestamp), int((recv_timestamp % 1) * (2**32)),  # Receive Timestamp (server)
            int(trans_timestamp), int((trans_timestamp % 1) * (2**32))  # Transmit Timestamp (server)
        )

        # Compute and append HMAC
        signature = generate_hmac(response)
        response_with_hmac = response + signature

        server.sendto(response_with_hmac, addr)  # Send response to client
        print(f"Responded to {addr}")

if __name__ == "__main__":
    ntp_server()

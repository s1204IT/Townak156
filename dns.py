#!/usr/bin/env python3
import os, socket, struct

DOMAIN = "townak.benesse.ne.jp"
UPSTREAM = "1.1.1.1"

def self_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((UPSTREAM, 53))
        return s.getsockname()[0]
    finally:
        s.close()

BIND = self_ip()
TARGET = BIND

def qname(data, off):
    labels = []
    while data[off]:
        n = data[off]
        labels.append(data[off + 1:off + 1 + n].decode("ascii", "ignore"))
        off += 1 + n
    return ".".join(labels), off + 1

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((BIND, 53))
    up = (UPSTREAM, 53)
    print("dns up", flush=True)
    while True:
        data, addr = s.recvfrom(4096)
        try:
            name, off = qname(data, 12)
        except Exception:
            continue
        if name.lower().rstrip(".") == DOMAIN:
            question = data[12:off + 4]
            ans = b"\xc0\x0c" + struct.pack(">HHIH", 1, 1, 60, 4) + socket.inet_aton(TARGET)
            resp = data[:2] + b"\x81\x80" + data[4:6] + b"\x00\x01\x00\x00\x00\x00" + question + ans
            s.sendto(resp, addr)
        else:
            s.sendto(data, up)
            try:
                r, _ = s.recvfrom(4096)
                s.sendto(r, addr)
            except Exception:
                pass

if __name__ == "__main__":
    main()

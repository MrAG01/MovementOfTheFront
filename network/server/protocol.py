import json
import struct


class Protocol:
    HEADER_FORMAT = '!Q'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    ENCODING_FORMAT = 'utf-8'

    @staticmethod
    def encode(data):
        str_data = json.dumps(data, separators=(',', ':'))
        bytes_data = str_data.encode(Protocol.ENCODING_FORMAT)
        return struct.pack(Protocol.HEADER_FORMAT, len(bytes_data)) + bytes_data

    @staticmethod
    def decode(raw_bytes):
        message_length = struct.unpack(Protocol.HEADER_FORMAT, raw_bytes[:Protocol.HEADER_SIZE])[0]
        total_size = message_length + Protocol.HEADER_SIZE
        message_str = raw_bytes[Protocol.HEADER_SIZE:total_size].decode(
            Protocol.ENCODING_FORMAT)
        return json.loads(message_str), total_size

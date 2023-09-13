from limekit.framework.core.engine.app_engine import EnginePart


class Endoding(EnginePart):
    name = "__encoding"
    B64_CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

    @classmethod
    def base64_encode(cls, data_: str):
        data = data_.encode("utf-8")
        binary_stream = "".join(bin(byte)[2:].zfill(8) for byte in data)

        padding_needed = len(binary_stream) % 6 != 0

        if padding_needed:
            # The padding that will be added later
            padding = b"=" * ((6 - len(binary_stream) % 6) // 2)

            # Append binary_stream with arbitrary binary digits (0's by default) to make its
            # length a multiple of 6.
            binary_stream += "0" * (6 - len(binary_stream) % 6)
        else:
            padding = b""

        # Encode every 6 binary digits to their corresponding Base64 character
        return (
            "".join(
                cls.B64_CHARSET[int(binary_stream[index : index + 6], 2)]
                for index in range(0, len(binary_stream), 6)
            ).encode()
            + padding
        )

    @classmethod
    def base64_decode(cls, encoded_data: str):
        # Make sure encoded_data is either a string or a bytes-like object
        if not isinstance(encoded_data, bytes) and not isinstance(encoded_data, str):
            msg = (
                "argument should be a bytes-like object or ASCII string, "
                f"not '{encoded_data.__class__.__name__}'"
            )
            raise TypeError(msg)

        # In case encoded_data is a bytes-like object, make sure it contains only
        # ASCII characters so we convert it to a string object
        if isinstance(encoded_data, bytes):
            try:
                encoded_data = encoded_data.decode("utf-8")
            except UnicodeDecodeError:
                raise ValueError(
                    "base64 encoded data should only contain ASCII characters"
                )

        padding = encoded_data.count("=")

        # Check if the encoded string contains non base64 characters
        if padding:
            assert all(
                char in cls.B64_CHARSET for char in encoded_data[:-padding]
            ), "Invalid base64 character(s) found."
        else:
            assert all(
                char in cls.B64_CHARSET for char in encoded_data
            ), "Invalid base64 character(s) found."

        # Check the padding
        assert len(encoded_data) % 4 == 0 and padding < 3, "Incorrect padding"

        if padding:
            # Remove padding if there is one
            encoded_data = encoded_data[:-padding]

            binary_stream = "".join(
                bin(cls.B64_CHARSET.index(char))[2:].zfill(6) for char in encoded_data
            )[: -padding * 2]
        else:
            binary_stream = "".join(
                bin(cls.B64_CHARSET.index(char))[2:].zfill(6) for char in encoded_data
            )

        data = [
            int(binary_stream[index : index + 8], 2)
            for index in range(0, len(binary_stream), 8)
        ]

        return bytes(data).decode("utf-8")

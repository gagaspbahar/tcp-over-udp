import lib.config as config

DATA_LIMIT = config.PAYLOAD_SIZE

def partition_data(data: bytes) -> list:
  array_of_data = []
  while len(data) > 0:
    if len(data) > DATA_LIMIT:
      array_of_data.append(data[:DATA_LIMIT])
      data = data[DATA_LIMIT:]
    else:
      array_of_data.append(data)
      data = b''
  return array_of_data

def join_data(data: list) -> bytes:
  return b''.join(data)
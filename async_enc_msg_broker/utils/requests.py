import json
import uuid

def request_handler(request:bytes):
    if len(request) < 4:
        return None
    
    request_bytes_len= int.from_bytes(request[0:4], 'big')
    request_bytes= request[4: 4 + request_bytes_len]
    yield request_bytes_len

    request_string= json.loads(request_bytes.decode('utf-8'))
    yield request_string.get('req_metadata')

    new_request= {
        'headers': request_string.get('headers'),
        'body': request_string.get('body'),
        'queue_name': request_string.get('queue_name')
    }
    
    new_request_bytes= json.dumps(new_request).encode('utf-8')
    new_request_bytes_len= len(new_request_bytes).to_bytes(4, 'big')

    yield new_request_bytes_len + new_request_bytes
    



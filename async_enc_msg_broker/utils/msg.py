import json 
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from typing import Dict, Literal, Any




@dataclass
class Message:
    
    body: str
    content_type: str= field(default="application/json")
    correlation_id: str | None= None
    scheduled_mode: Literal['interval', 'date', 'cron']= field(default='interval')
    kwargs: Dict[str, Any]= field(default_factory=dict)

    
    def __bytes__(self):

        metadata= {
            'content-type': self.content_type,
            'correlation_id': self.correlation_id
        }

        message= {
            'metadata': metadata,
            'body': self.body
        }

        message_bytes= json.dumps(message).encode('utf-8')
        message_bytes_len= len(message_bytes).to_bytes(4, 'big')

        return message_bytes_len + message_bytes
    


def handle_response(message: bytes) -> dict:
    status= ""

    if len(message) < 4:
        return None
    
    message_bytes_len= int.from_bytes(message[0:4], 'big')
    message_bytes= message[4: 4 + message_bytes_len]    

    try:
        message_string= json.loads(message_bytes.decode('utf-8'))

        status= '-- deserialised successfully --'

    except json.JSONDecodeError as e:
        status= f'-- deserialisation failed -- \n{e}'

    if message_string.get('kwargs'):
        expiry= message_string.get('kwargs')['exp']
        time_passed= expiry - datetime.now(timezone.utc).timestamp()
        
        if time_passed > 0:
            return {
                'status': status,
                'headers': message_string.get('headers'),
                'body': message_string.get('body')
            }
        else:
            return "message is expired"
    else:
        return {
                'status': status,
                'headers': message_string.get('headers'),
                'body': message_string.get('body')
            }




        
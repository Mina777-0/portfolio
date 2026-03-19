import struct, msgspec

class CircularBuffer:
    def __init__(self, size:int):
        self.buffer= bytearray(size)
        self.mv= memoryview(self.buffer)
        self.head= 0
        self.tail= 0
        self.count= 0
        self.size= size
        self.FROMAT= '!IddQ'
        self.PACKET_SIZE= struct.calcsize(self.FROMAT)

    def write_to(self):
        return self.mv[self.tail: ]
    
    def did_write(self, nbytes):
            
        self.tail= (self.tail + nbytes) % self.size
        self.count += nbytes

    def peek(self):
        return self.mv[self.head: self.head + self.PACKET_SIZE]

    def advance(self):
        self.head = (self.head + self.PACKET_SIZE) % self.size
        self.count -= self.PACKET_SIZE

        # Check the remaining chunks
        left_chunck= self.size - self.tail
        if self.PACKET_SIZE > left_chunck:
            self.tail= (self.tail + left_chunck) % self.size
            self.head= (self.head + left_chunck) % self.size
            self.count= 0




class PriceSchema(msgspec.Struct, gc=False):
    # gc=Fasle means no cyclic garbage collection. No use of __dict__
    # implements custom C-level structs for its types. 
    symbol_id:int 
    bid_price:float
    ask_price:float
    volume:int 
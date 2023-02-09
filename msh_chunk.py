import struct
import re


class Chunk:
    def __init__(self, data: bytes | str, chunk_start=0):
        if isinstance(data, str):
            raw_data = open(data, 'rb').read()
        else:
            raw_data = data

        data_start = chunk_start + 8
        header, self.length = struct.unpack('<4sI', raw_data[chunk_start:data_start])
        self.header = header.decode()
        chunk_end = data_start + self.length
        chunk_data = raw_data[data_start:chunk_end]

        pattern_once = re.compile('HEDR|FINF|SINF|CAMR|SEGM|CLTH|ANM2|LGTP|LGTI|LGTS|MATD|MODL')
        pattern_many = re.compile('MATL|MSH2|GEOM')
        if pattern_once.match(self.header):
            self.data = {}
            offset = data_start
            while offset < chunk_end:
                subchunk = Chunk(raw_data, offset)
                offset += subchunk.length + 8
                self.data[subchunk.header] = subchunk
        elif pattern_many.match(self.header):
            self.data = []
            offset = data_start
            if self.header == 'MATL':
                offset += 4
            while offset < chunk_end:
                subchunk = Chunk(raw_data, offset)
                offset += subchunk.length + 8
                self.data.append(subchunk)
        else:
            self.data = chunk_data

    def __getitem__(self, key):
        return self.data[key]

    def __repr__(self):
        data_repr = '<bytes>'
        if isinstance(self.data, dict):
            data_repr = [self[x] for x in self.data]
        return f'Chunk(header={self.header}, length={self.length}, data={data_repr})'
    
    def tree(self, indent=0):
        space = ' ' * indent
        out = space + self.header + ':'

        pattern_txt = re.compile('FINF|TX[0-9]D|PRFX|PRNT|CTEX|NAME')
        pattern_int = re.compile('SHVO|MTYP|MNDX|FLGS|MATI')
        if pattern_txt.match(self.header):
            out += ' ' + self.data.decode().rstrip('\0')
        elif pattern_int.match(self.header):
            out += ' ' + str(struct.unpack('<I', self.data)[0])
        elif isinstance(self.data, dict):
            for key in self.data:
                out += '\n' + self[key].tree(indent + 4)
        elif isinstance(self.data, list):
            for subchunk in self.data:
                out += '\n' + subchunk.tree(indent + 4)
        elif self.length <= 12:
            out += ' ' + ' '.join(f'{x:02x}' for x in self.data)
        else:
            out += f' <len: {self.length}>'
        return out
    
    def filter(self, key):
        if isinstance(self.data, dict):
            return [self[x] for x in self.data if x == key]
        elif isinstance(self.data, list):
            return [x for x in self.data if x.header == key]
        return []
    
    def filter_all(self, key):
        results = self.filter(key)
        if isinstance(self.data, dict):
            for x in self.data:
                results.extend(self[x].filter_all(key))
        elif isinstance(self.data, list):
            for x in self.data:
                results.extend(x.filter_all(key))
        return results
    
    def data_len(self):
        return struct.unpack('<I', self.data[:4])[0]

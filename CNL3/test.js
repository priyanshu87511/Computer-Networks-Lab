const struct = require('python-struct');

// Define the packed binary data
// const packedData = Buffer.from([42, 0, 65, 66, 64, 9, 33, 71, 235, 81]);

// Define the format string (matching the format used for packing)
const format = '!HBBII';
const packedData = struct.pack(format, [12, 5, 14, 17, 22]);
console.log(packedData);


const combined1 = Buffer.concat([Buffer.from(packedData), Buffer.from('data2')]);
console.log(combined1);

const combined = combined1.toString();
console.log(combined);

const backString = combined1.slice(struct.sizeOf(format));
console.log(backString.toString());

const obj = combined1.slice(0, struct.sizeOf(format));
console.log(struct.unpack(format, obj));

// const combinedmessage = combined.toString();
// console.log(combinedmessage);
// const unpackedData = struct.unpack(format, packedData);
// console.log(unpackedData);
// Unpack the binary data into a JavaScript object
// const unpackedData = binaryPack.unpack(format, packedData);

// Print the unpacked data
// console.log(unpackedData);
/*
return struct.pack('!HBBII', MAGIC_NUMBER, VERSION, command, sequence, session_id)
magic, version, command, sequence, session_id = struct.unpack('!HBBII', data[:header_size])
*/

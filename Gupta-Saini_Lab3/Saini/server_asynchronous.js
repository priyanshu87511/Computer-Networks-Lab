const net = require('net');
const { exit } = require('process');
const struct = require('python-struct');
const readline = require('readline');

const IP = '127.0.0.1'; // You can specify your desired IP address here
const PORT = parseInt(process.argv[2]);
const SIZE = 1024;
const FORMAT = 'utf-8';
const PACK_FORMAT = '!HBBII';
const TERMINATION_MSG = 'GOODBYE';
const ALIVE_MSG = 'ALIVE';
const START_MSG = 'HELLO';
const MAGIC_NUMBER = 50273;
const VERSION = 1;
const CLIENT_TIMEOUT = 15000; // 60 seconds in milliseconds

// returns buffer
function getHeader(format, magic, version, command, seqNum, sessionId) {
    return struct.pack(format, magic, version, command, seqNum, sessionId);
}

function getMessage(header, data) {
    return Buffer.concat([Buffer.from(header), Buffer.from(data)]);
}


function unpackHeader(format, message) {
    const headerSize = struct.sizeOf(format);
    const headerBuffer = message.slice(0, headerSize);
    return struct.unpack(format, headerBuffer);
}

function unpackData(format, message) {
    const headerSize = struct.sizeOf(format);
    const dataBuffer = message.slice(headerSize);
    return dataBuffer.toString();
}

function printToConsole(sessionId, sequenceNumber, message) {
    try {
        let result = '';
        result += `0x${sessionId.toString(16)} `;
        if (sequenceNumber !== '') {
            result += `[${sequenceNumber}] `;
        }
        result += message;
        console.log(result);
    } catch (error) {
        
    }
}

function addressToString(address, port) {
    return `[${address}, ${port}]`;
}

function takeInput() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });


    function takeInputAndSendMessage() {
        rl.question('', (input) => {
            if (input === 'q') {
                closeServer();
            }
            takeInputAndSendMessage();
        });
    }
    takeInputAndSendMessage();
}

function getCommand(data) {
    let res = 1;
    if (data === START_MSG) {
        res = 0;
    } else if (data === ALIVE_MSG) {
        res = 2;
    } else if (data === TERMINATION_MSG) {
        res = 3;
    }
}

const clients = new Map();
const socketToSessionId = new Map();

function terminateConnection(socket) {
    // clearInterval(timer);
    // socket.write(TERMINATION_MSG, FORMAT);
    const command = getCommand(input);
    const header = getHeader(PACK_FORMAT, MAGIC_NUMBER, VERSION, command, sequence_number, sessionId);
    const MSG = getMessage(header, TERMINATION_MSG);
    sendMessage(MSG);
    socket.end();
}

function handleClient(socket) {
    let connected = true;
    let sequenceNumber = 0;
    let lastActivityTime = Date.now();

    const timer = setInterval(() => {
        const currentTime = Date.now();
        if (currentTime - lastActivityTime >= CLIENT_TIMEOUT) {
            terminateConnection(socket);
        }
    }, CLIENT_TIMEOUT);

    socket.on('data', (data) => {
        // Update last activity time
        lastActivityTime = Date.now();

        const msg = unpackData(PACK_FORMAT, data);
        const header = unpackHeader(PACK_FORMAT, data);
        const [message_magicNo, message_version, message_command, message_seqNo, message_sessionId] = header;
        socketToSessionId.set(addressToString(socket.remoteAddress, socket.remotePort), message_sessionId);


        if (message_magicNo !== MAGIC_NUMBER || message_version !== VERSION) {
            // message discarded
        } else if (message_seqNo === sequenceNumber - 1) {
            // discarded
            printToConsole(message_seqNo, message_seqNo, 'Duplicate packet');
        } else if (message_seqNo < sequenceNumber - 1) {
            printToConsole(message_seqNo, message_seqNo, 'Protocol Error');
            terminateConnection(socket);
        } else {
            if (message_seqNo > sequenceNumber) {
                // packets dropped
                for (let i = sequenceNumber; i < message_seqNo; i++) {
                    printToConsole(message_sessionId, i, 'Lost packet!');
                }
            }
            let toPrint = msg;
            if (toPrint === START_MSG && message_seqNo === 0) {
                toPrint = 'Session created';
            } else if (toPrint === TERMINATION_MSG) {
                toPrint = 'GOODBYE from client';
            }
            // console.log(`0x${message_sessionId.toString(16)} [${sequenceNumber}] ${toPrint}`);
            printToConsole(message_sessionId, sequenceNumber, toPrint);

            if (msg !== START_MSG && msg !== TERMINATION_MSG) {
                const command = 2;
                const header = getHeader(PACK_FORMAT, MAGIC_NUMBER, VERSION, command, sequenceNumber, message_sessionId);
                const MSG = getMessage(header, ALIVE_MSG);
                socket.write(MSG, FORMAT);
            } else if (msg === TERMINATION_MSG) {
                const command = 3;
                const header = getHeader(FORMAT, MAGIC_NUMBER, VERSION, command, sequenceNumber, message_sessionId);
                const MSG = getMessage(header, TERMINATION_MSG);
                socket.write(MSG, FORMAT);
                clearInterval(timer); // Clear the timer when terminating the connection
                clients.delete(socket);
                socket.end();
            }
            sequenceNumber = message_seqNo + 1;
        }
    });

    socket.on('end', () => {
        printToConsole(socketToSessionId.get(addressToString(socket.remoteAddress, socket.remotePort)), '', 'Session closed');
    });

    socket.on('error', (err) => {
        printToConsole(socketToSessionId.get(addressToString(socket.remoteAddress, socket.remotePort)), '', err.message);
    });

    // Store the socket in the clients map for tracking
    clients.set(socket, timer);
    // takeInputAndSendMessage();
}

const server = net.createServer(handleClient);

server.listen(PORT, IP, () => {
    console.log(`Waiting on port ${PORT}...`);
    takeInput();
});

server.on('error', (err) => {
    console.error(`Server error: ${err.message}`);
});

function closeServer() {
    console.log("Closing server...");

    for (const socket of [...clients.keys()]) {
        const command = 3;
        const sessionId = socketToSessionId.get(addressToString(socket.remoteAddress, socket.remotePort));
        const header = getHeader(PACK_FORMAT, MAGIC_NUMBER, VERSION, command, 404, sessionId);
        const MSG = getMessage(header, TERMINATION_MSG);
        socket.write(MSG);
        // socket.end();
    }

    // Close the server (stop accepting new connections)
    server.close(() => {
        process.exit(0); // Terminate the Node.js process
    });
}

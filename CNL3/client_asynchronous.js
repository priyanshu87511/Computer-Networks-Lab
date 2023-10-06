const net = require('net');
const { exit } = require('process');
const readline = require('readline');
const struct = require('python-struct');

const SERVER_IP = '127.0.0.1'; // Server IP address
const SERVER_PORT = parseInt(process.argv[2]);
const CLIENT_NAME = 'Client1'; // Replace with your client's name
const START_MSG = 'HELLO';
const ALIVE_MSG = 'ALIVE';
const TERMINATION_MSG = 'GOODBYE';
const FORMAT = 'utf-8';
const PACK_FORMAT = '!HBBII';
const MAGIC_NUMBER = 50273;
const VERSION = 1;

const client = new net.Socket();
let sequence_number = 0;
let lastMessageTime = Date.now(); // Initialize the last message time

const TIMEOUT_DURATION = 15000; // Set the timeout duration in milliseconds (e.g., 60 seconds)

function generateSessionId() {
  return Math.floor(Math.random() * Math.pow(2, 31));
}

// returns buffer
function getHeader(format, magic, version, command, seqNum, sessionId) {
  return struct.pack(format, magic, version, command, seqNum, sessionId);
}

function getMessage(header, data) {
  return Buffer.concat([Buffer.from(header), Buffer.from(data)]);
}

function unpackData(format, message) {
  const headerSize = struct.sizeOf(format);
  const dataBuffer = message.slice(headerSize);
  return dataBuffer.toString();
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

client.connect(SERVER_PORT, SERVER_IP, () => {
  console.log(`Connected to server at ${SERVER_IP}:${SERVER_PORT}`);
  const sessionId = generateSessionId();
  startSession(sessionId);
});

client.on('data', (data) => {
  const message = unpackData(PACK_FORMAT, data);
  console.log(`[SERVER]: ${message}`);
  if (message === TERMINATION_MSG) {
    client.destroy();
  }
  // Update the last message time when a message is received
  lastMessageTime = Date.now();
});

client.on('close', () => {
  console.log('Connection closed');
  exit();
});

client.on('error', (err) => {
  console.error(`Client error: ${err.message}`);
});

function sendMessage(message) {
  client.write(message);
}

function startSession(sessionId) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  // Function to send a message
  function takeInputAndSendMessage() {
    if (sequence_number === 0) {
      const command = getCommand(START_MSG);
      const header = getHeader(PACK_FORMAT, MAGIC_NUMBER, VERSION, command, sequence_number, sessionId);
      const MSG = getMessage(header, START_MSG);
      sendMessage(MSG);
      sequence_number++;
      takeInputAndSendMessage();
    } else {
      rl.question('', (input) => {
        const command = getCommand(input);
        const header = getHeader(PACK_FORMAT, MAGIC_NUMBER, VERSION, command, sequence_number, sessionId);
        const MSG = getMessage(header, input);
        sendMessage(MSG);
        sequence_number++;
        // Continue taking input in a loop
        takeInputAndSendMessage();
      });
    }
  }
  let message = START_MSG;
  takeInputAndSendMessage(); // Start the input loop

  // Check for inactivity and close the connection if necessary
  function checkInactivity() {
    const currentTime = Date.now();
    const timeSinceLastMessage = currentTime - lastMessageTime;

    if (timeSinceLastMessage >= TIMEOUT_DURATION) {
      console.log(`Connection timed out due to inactivity.`);
      client.destroy(); // Close the connection
      exit();
    }

    // Schedule the next check
    setTimeout(checkInactivity, TIMEOUT_DURATION - timeSinceLastMessage);
  }

  // Start checking for inactivity
  checkInactivity();
}

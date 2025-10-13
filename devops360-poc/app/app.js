const http = require('http');
const os = require('os');
const port = process.env.PORT || 8080;


http.createServer((req, res) => {
if (req.url === '/health') {
const load = os.loadavg();
const freeMemMB = Math.round(os.freemem() / 1024 / 1024);
const totalMemMB = Math.round(os.totalmem() / 1024 / 1024);
res.writeHead(200, {'Content-Type':'application/json'});
res.end(JSON.stringify({
message: "DevOps360 demo app running",
host: os.hostname(),
env: process.env.ENV_NAME || 'staging',
time: new Date().toISOString(),
load, freeMemMB, totalMemMB
}));
return;
}
res.writeHead(200, {'Content-Type':'text/plain'});
res.end(`Hello from DevOps360 demo — host: ${os.hostname()}\n`);
}).listen(port, () => console.log(`Server running on ${port}`));
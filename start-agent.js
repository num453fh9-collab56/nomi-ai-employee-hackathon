const { spawn } = require('child_process');

const python = spawn('python', ['main.py', '--synthesis'], {
    stdio: 'inherit',
    shell: true
});

python.on('exit', (code) => {
    process.exit(code);
});

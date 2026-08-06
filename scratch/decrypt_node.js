
const crypto = require('crypto');
const hex = 'c9a9fc61a2940b4575086201867a7b4e5385fbea0e8eb0edab0600371f8e217831175ceef7bd28ae4f4ca6936889c7a33e7746586b3914a3c923785165d83309dbd9401d6b64384edb043bcafb63f78b216a24c21f9db61da5f680782804bfdb71423c369d51c50d9d9459d7d70b5bcb8d1c6f85c21df1982d72bff4ef87af5284e8a9cf8c4a539e3a0bfa9fc7ae0512005bbcb8f5868e478e8ee10bcbd4802fd9ab5123e55b2830c8d3fcdd620935c79a76b100841adb387a1ce529cb3ffbc796d90a825b09bbe5ed5e3f0b15d294999fcc44b24ea83597cf8932725496232c';
const keys = ['ftp-simple', 'humy2833', 'vscode', 'antigravity', 'Sunfra#321', 'Kusum@2026Bb!'];

for (const key of keys) {
    try {
        const decipher = crypto.createDecipher('aes-256-cbc', key);
        let dec = decipher.update(hex, 'hex', 'utf8');
        dec += decipher.final('utf8');
        console.log('KEY SUCCESS:', key);
        console.log(dec);
        break;
    } catch(e) {
        // try decipheriv
    }
}

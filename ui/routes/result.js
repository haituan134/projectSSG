var express = require('express');
var router = express.Router();
var formidable = require('formidable');
var fs = require('fs');
var path = require('path');
var { spawn } = require('child_process');
var readline = require('readline');

router.post('/', (req, res) => {
    let form = new formidable.IncomingForm();
    form.parse(req);
    form.on('file', (name, file) => {
        let cnt = 0;
        let p = path.join(__dirname, '../public/images/');
        let child = spawn('python', ['../app.py', file.path]);
        readline.createInterface({
            input: child.stdout,
            terminal: false
        }).on('line', (line) => {
            fs.rename(line, p + 'img' + cnt, (err) => {
                console.log(err);
            });
            cnt += 1;
        }).on('close', () => {
            console.log(cnt);
            let imagePath = [];
            for (let i = 0; i < cnt; ++i) {
                imagePath.push('/images/img' + i);
            }
            res.render('index', {
                title: 'Project SSG',
                imagePath: imagePath,
                result: true
            });
        });
    });
});

module.exports = router;
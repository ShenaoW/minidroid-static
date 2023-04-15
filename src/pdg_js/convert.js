module.exports = {
    frm6to5: frm6to5,
};

var babel = require("@babel/core")
var fs = require("fs");
var process = require("process");


function frm6to5(js) {
    var es6Code = fs.readFileSync(js).toString('utf-8');
    const options = {
        presets: ["@babel/preset-env"]
      };
    try {
        var result = babel.transformSync(es6Code, options);
    } catch(e) {
        console.error(js, e);
        process.exit(1);
    }
    es5Code = result["code"]
    fs.writeFile(js, es5Code, function (err) {
        if (err) {
            console.error(err);
        }
    });

    return es5Code;
}

frm6to5(process.argv[2]);

const fs = require('fs');
const html = fs.readFileSync('player.html', 'utf-8');
const scriptMatches = html.match(/<script[\s\S]*?<\/script>/gi);
let errorCount = 0;
scriptMatches.forEach((s, idx) => {
    if (s.includes('src=')) return;
    const js = s.replace(/<script[^>]*>/i, '').replace(/<\/script>/i, '');
    try {
        new Function(js);
        console.log(`Script block ${idx} is 100% syntactically VALID (${js.length} characters)`);
    } catch (e) {
        console.error(`Script block ${idx} SYNTAX ERROR:`, e.message);
        errorCount++;
    }
});
if (errorCount === 0) {
    console.log("SUCCESS: All JavaScript code is 100% syntactically valid!");
    process.exit(0);
} else {
    process.exit(1);
}

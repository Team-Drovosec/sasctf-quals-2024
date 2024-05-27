const puppeteer = require('puppeteer');

function sleep(s){
    return new Promise((resolve)=>setTimeout(resolve, s))
}

const initBrowser = puppeteer.launch({
    executablePath: "/usr/bin/chromium-browser",
    headless: true,
    args: [
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-gpu',
        '--no-gpu',
        '--disable-default-apps',
        '--disable-translate',
        '--disable-device-discovery-notifications',
        '--disable-software-rasterizer',
        '--disable-xss-auditor'
    ],
    ipDataDir: '/home/bot/data/',
    ignoreHTTPSErrors: true
});

const visit = async (urlToVisit) => {
    const browser = await initBrowser;
    const context = await browser.createBrowserContext()
    try {
        const page = await context.newPage();

        console.log(`Bot is visiting ${urlToVisit}`)
        await page.goto(urlToVisit, {
            waitUntil: 'networkidle2'
        });
        await sleep(4000);

        console.log("Closing browser...")
        await context.close()
        return true;
    } catch (e) {
        console.error(e);
        await context.close();
        return false;
    }
}

visit('https://einabe.local/admin/review_booking/' + process.argv[2]).then(() => {console.log('Well done!')});
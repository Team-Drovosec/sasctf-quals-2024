let barCount = 60;
var date = luxon.DateTime.now();

let ctx = document.getElementById('chart').getContext('2d');
ctx.canvas.width = 0.70 * window.innerWidth;
ctx.canvas.height = 0.40 * window.innerHeight;

let barData = getData(barCount);
function lineData() { return barData.map(d => { return { x: d.x, y: d.c} }) };

function generateRandomToken() {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const charactersLength = characters.length;
    for (let i = 0; i < 3; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

let chart = new Chart(ctx, {
	type: 'candlestick',
	data: {
		datasets: [{
			label: generateRandomToken() + '/USD',
			data: barData
		}]
	},
	options: {
        animation: {
            duration: 0
        },
        hover: {
            animationDuration: 0
        },
        responsiveAnimationDuration: 0
    }
});

function randomNumber(min, max) {
	return Math.random() * (max - min) + min;
}

function getBar(lastClose) {
	let open = lastClose;
	let close = randomNumber(open * 0.8, open * 1.2499).toFixed(2);
	let high = randomNumber(Math.max(open, close), Math.max(open, close) * 1.1).toFixed(2);
	let low = randomNumber(Math.min(open, close) * 0.9, Math.min(open, close)).toFixed(2);
	return {
		x: date.valueOf(),
		o: open,
		h: high,
		l: low,
		c: close
	};

}

function getData(count) {
	let data = [getBar(32500)];
	while (data.length < count) {
		date = date.plus({seconds: 2});
		data.push(getBar(data[data.length - 1].c));
	}
	return data;
}

setInterval(() => {
	date = date.plus({seconds: 2});
	barData.shift()
	barData.push(getBar(barData[barData.length - 1].c))
	chart.config.data.datasets[0].data = barData
	chart.update();
}, 2000)
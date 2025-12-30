// Demo kỹ thuật bất đồng bộ với Callback trong JavaScript

function fakeTask(name, duration, callback) {
    console.log(`${name} bắt đầu...`);
    setTimeout(() => {
        console.log(`${name} hoàn thành sau ${duration} giây.`);
        if (callback) callback();
    }, duration * 1000);
}

function runWithCallback() {
    console.log("\n--- Mô phỏng với Callback ---");
    let completed = 0;
    const total = 5;
    for (let i = 1; i <= total; i++) {
        fakeTask(`Task-${i}`, 2, () => {
            completed++;
            if (completed === total) {
                console.log("Tất cả tác vụ đã hoàn thành (callback)");
            }
        });
    }
}

runWithCallback();

// Demo kỹ thuật bất đồng bộ với Promise
function fakeTaskPromise(name, duration) {
    return new Promise((resolve) => {
        console.log(`${name} (promise) bắt đầu...`);
        setTimeout(() => {
            console.log(`${name} (promise) hoàn thành sau ${duration} giây.`);
            resolve();
        }, duration * 1000);
    });
}

async function runWithPromise() {
    console.log("\n--- Mô phỏng với Promise.all ---");
    const tasks = [];
    for (let i = 1; i <= 5; i++) {
        tasks.push(fakeTaskPromise(`Task-${i}`, 2));
    }
    await Promise.all(tasks);
    console.log("Tất cả tác vụ đã hoàn thành (Promise)");
}

// Demo kỹ thuật bất đồng bộ với async/await
async function fakeTaskAsync(name, duration) {
    console.log(`${name} (async/await) bắt đầu...`);
    await new Promise((resolve) => setTimeout(resolve, duration * 1000));
    console.log(`${name} (async/await) hoàn thành sau ${duration} giây.`);
}

async function runWithAsyncAwait() {
    console.log("\n--- Mô phỏng với async/await ---");
    const tasks = [];
    for (let i = 1; i <= 5; i++) {
        tasks.push(fakeTaskAsync(`Task-${i}`, 2));
    }
    await Promise.all(tasks);
    console.log("Tất cả tác vụ đã hoàn thành (async/await)");
}

// Gọi các hàm Promise và async/await
runWithPromise();
runWithAsyncAwait();

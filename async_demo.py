# Import cần được đặt ở đầu file
import time
import threading
import asyncio

# Hàm mô phỏng tác vụ tốn thời gian (giả lập tải dữ liệu)
def fake_task(name, duration=1):
	print(f"{name} bắt đầu...")
	time.sleep(duration)
	print(f"{name} hoàn thành sau {duration} giây.")

# Hàm mô phỏng bất đồng bộ với asyncio
async def async_fake_task(name, duration=1):
	print(f"{name} (async) bắt đầu...")
	await asyncio.sleep(duration)
	print(f"{name} (async) hoàn thành sau {duration} giây.")

# Mô phỏng chạy song song nhiều tác vụ bằng threading
def run_with_threading():
	print("\n--- Mô phỏng với threading ---")
	start = time.time()
	threads = []
	for i in range(5):
		t = threading.Thread(target=fake_task, args=(f"Task-{i+1}", 2))
		threads.append(t)
		t.start()
	for t in threads:
		t.join()
	print(f"Tổng thời gian (threading): {time.time() - start:.2f} giây")

# Mô phỏng chạy song song nhiều tác vụ bằng async/await (asyncio)
def run_with_asyncio():
	print("\n--- Mô phỏng với async/await (asyncio) ---")
	async def main():
		start = time.time()
		tasks = [async_fake_task(f"Task-{i+1}", 2) for i in range(5)]
		await asyncio.gather(*tasks)
		print(f"Tổng thời gian (asyncio): {time.time() - start:.2f} giây")
	asyncio.run(main())

# Hàm chạy tuần tự để so sánh
def run_sequential():
	print("\n--- Mô phỏng chạy tuần tự ---")
	start = time.time()
	for i in range(5):
		fake_task(f"Task-{i+1}", 2)
	print(f"Tổng thời gian (tuần tự): {time.time() - start:.2f} giây")

# Hàm main để chạy tất cả các mô phỏng
if __name__ == "__main__":
	run_sequential()
	run_with_threading()
	run_with_asyncio()

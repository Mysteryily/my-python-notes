import threading
import time

from client_mgr import CClientMgr
from server_mgr import CServerMgr


def client_on_message(data: dict):
    """客户端收到数据后的业务处理"""
    if data.get("type") == "server_push":
        print(f"  [Client收到推送] seq={data.get('seq')}, msg={data.get('message')}")
    else:
        time.sleep(0.05)
        checksum = hash(str(data)) % 1000000
        print(f"  [Client业务] seq={data.get('seq')}, checksum={checksum}")


def server_on_message(data: dict) -> dict:
    """服务端收到客户端数据后的业务处理"""
    time.sleep(0.1)
    n = data.get("seq", 0) % 1000
    computed = sum(i * i for i in range(n * 100))
    print(f"  [Server业务] seq={data.get('seq')}, computed={computed}")
    return {
        "status": "processed",
        "seq": data.get("seq"),
        "computed": computed,
        "timestamp": time.time()
    }


def client_producer(client_mgr: CClientMgr, running: threading.Event):
    """独立线程：每秒生成并发送业务数据"""
    seq = 0
    while running.is_set():
        seq += 1
        data = {
            "seq": seq,
            "timestamp": time.time(),
            "type": "business_data",
            "payload": f"msg_{seq}"
        }
        client_mgr.send(data)
        time.sleep(1)


def server_producer(server_mgr: CServerMgr, running: threading.Event):
    """独立线程：每3秒从服务端主动推送数据"""
    seq = 0
    while running.is_set():
        seq += 1
        data = {
            "seq": seq,
            "message": f"server_push_{seq}",
            "timestamp": time.time(),
            "type": "server_push"
        }
        server_mgr.send(data)
        time.sleep(3)


def main():
    client_mgr = CClientMgr.get_instance()
    server_mgr = CServerMgr.get_instance()

    client_mgr.set_on_message(client_on_message)
    server_mgr.set_on_message(server_on_message)

    producer_running = threading.Event()
    producer_running.set()

    print("Starting client (background daemon thread)...")
    client_mgr.start()
    print("Starting client producer (background thread)...")
    cli_thread = threading.Thread(
        target=client_producer, args=(client_mgr, producer_running), daemon=True
    )
    cli_thread.start()
    print("Starting server producer (background thread)...")
    srv_thread = threading.Thread(
        target=server_producer, args=(server_mgr, producer_running), daemon=True
    )
    srv_thread.start()
    print("Starting server (main thread)...")
    try:
        server_mgr.start()
    except KeyboardInterrupt:
        pass
    finally:
        producer_running.clear()
        server_mgr.stop()
        client_mgr.stop()
        print("All stopped.")


if __name__ == '__main__':
    main()

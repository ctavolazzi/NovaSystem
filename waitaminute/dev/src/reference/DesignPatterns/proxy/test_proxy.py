from proxy import RealSubject, Proxy, client_code

def test_real_subject():
    print("Testing RealSubject:")
    real_subject = RealSubject()
    client_code(real_subject)

def test_proxy():
    print("\nTesting Proxy:")
    real_subject = RealSubject()
    proxy = Proxy(real_subject)
    client_code(proxy)

def main():
    test_real_subject()
    test_proxy()

if __name__ == "__main__":
    main()

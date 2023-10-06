import namespace_package as nsp
from namespace_package import package1
from namespace_package import tests

if __name__ == "__main__":
    package1.main.main()
    tests.test()
    nsp.test()
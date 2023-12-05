from facade import NovaSystemFacade, client_code

def test_novasystem_facade():
    # Creating the Facade instance
    novasystem_facade = NovaSystemFacade()

    # Simulating client interaction with the facade
    print("Testing NovaSystem Facade:")
    client_code(novasystem_facade)

def main():
    test_novasystem_facade()

if __name__ == "__main__":
    main()

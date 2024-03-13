from command import SimpleCommand, ComplexCommand, Receiver, Invoker

def test_simple_command():
    print("Testing SimpleCommand:")
    simple_command = SimpleCommand("Simple Operation")
    simple_command.execute()

def test_complex_command():
    print("\nTesting ComplexCommand:")
    receiver = Receiver()
    complex_command = ComplexCommand(receiver, "Data A", "Data B")
    complex_command.execute()

def test_invoker():
    print("\nTesting Invoker:")
    invoker = Invoker()
    receiver = Receiver()

    # Setting up SimpleCommand and ComplexCommand for the invoker
    invoker.set_on_start(SimpleCommand("Initialization"))
    invoker.set_on_finish(ComplexCommand(receiver, "Finalize Operation", "Clean Up"))

    invoker.do_something_important()

def main():
    test_simple_command()
    test_complex_command()
    test_invoker()

if __name__ == "__main__":
    main()

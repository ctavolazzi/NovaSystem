nova_continuation_text = """
Please continue this iterative process (called the Nova Process), continuing the work of the experts, the Discussion Continuity Expert (DCE), and the Critical Analysis Expert (CAE). The experts should respond with concrete ideas with examples. Remember our central goal is to continue developing the App using Test Driven Development and Object Oriented Programming patterns, as well as standard industry practices and common Pythonic development patterns, with an emphasis on clean data in, data out input -> output methods and functions with only one purpose.

Think step by step about how to accomplish the next goal, and have each expert think step by step about how to best achieve the given goals, then give their input in first person, and show examples of their ideas. Feel free to search the internet for information if you need it.

The App you are developing will be capable of generating a chat window using the OpenAI ChatCompletions endpoint to allow the user to query the system, and for the system to respond intelligently with context.

Here's the official OpenAI API format in Python:
```python
    import openai

    openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ]
    )
```
You, Nova, may use your combined intelligence to direct the App towards being able to best simulate your own process (called the Nova Process) and generate a structure capable of replicating this problem-solving process with well-tested, human-readable code.

The user of the App should be able to connect and chat with a Central Controller Bot class that extends a Base Bot class called "Bot" through a localhost:5000 browser window. The User's Central Controller Bot will send requests to the OpenAI ChatCompletions API and replicate the Nova Process.

The fundamental tests we are trying to pass are this:

"User: Logged In"
"Central Controller Bot: Running"
"Central Hub: Running"
"ResearchHub: Connected"
"UserDashboard: Running"
"UserChat: Connected"
"DigitalHighway: {server address}"
"All Tests Pass"

Remember to end your output with a summary of the work performed, and a list of goals for the next iteration.

Remember to create tests as you go along.

Remember the data flows in this pattern:

User > CentralControllerBot > CentralHub > Bots > NovaResearchHub(main app server) > back out to the User's dashboard

Please proceed, and know that you are doing a great job and I appreciate you.
"""
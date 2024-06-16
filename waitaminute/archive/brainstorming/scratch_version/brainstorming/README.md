<<<<<<< HEAD
# Nova Process: A Next-Generation Problem-Solving Framework for GPT-4 or Comparable LLM

Welcome to Nova Process, a pioneering problem-solving method developed by AIECO that harnesses the power of a team of virtual experts to tackle complex problems. This open-source project provides an implementation of the Nova Process utilizing ChatGPT, the state-of-the-art language model from OpenAI.

> [!FYI] This is a work in progress. Please feel free to make a pull request.
> > I am one person developing my own SDK for fun and learning. I am not affiliated with OpenAI in any way. I am not a professional developer. I am a hobbyist. I am not a professional programmer. Most of the code I write should never be used in a production environment.
> > You do not need my permission to use this code in your projects. BUT:
> > If you do use it, understand that it is GNU licensed, meaning you will need to make your project open source as well.
> > I am not responsible for any damages or losses that may occur from using this code. Use at your own risk.

> [!WARNING] THIS IS NOT A PRODUCTION-READY SDK. IT IS A WORK IN PROGRESS. USE AT YOUR OWN RISK.
=======
<<<<<<< HEAD
# NovaSystem: A Next-Generation Problem-Solving Framework for GPT-4 or Comparable LLM

Welcome to the NovaSystem, a pioneering problem-solving method and open source project developed by AIECO that harnesses the power of a team of virtual AI experts working together to respond to user requests. 


## How does it work?

This open source project provides an implementation of the Nova Process utilizing ChatGPT and the OpenAI API, the state-of-the-art language models GPT-3.5-Turbo and GPT-4 from OpenAI, and is currently being engineered to use LangChain and HuggingFace to extend its AI API capabilities into a fully autonomous and transparent self-training API aggregator.

We've been calling it a **"dynagenetic"** processing system ("dyna" - dynamic, "genetic" - generated and evolving). 

The NovaSystem runs permutations in an iterative process to **"version-bake"** a solution to a user query.

It writes records of its attempts in natrual language stored in markdown files in an Obsidian vault.

This allows for two very important things:

⤵️

### 1) NovaSystem stores its work as markdown files

No more obtuse or difficult filetypes. NovaSystem uses markdown formatting to ensure end-to-end utility and parsabiility.

### 2) NovaSystem's work is natively machine and human-readable

No more black boxes. No matter how complex your solution gets, NovaSystem will keep track of how it got there, so you can build what you need to build, fasteer and safer, with more data behind you every step of the way.



## Why does it matter?

### **One big problem with AI is it hallucinates.**

NovaSystem generates lots of data. But it doesn't matter how much data your program creates if it's inaccurate.

*How can you trust that what your AI says is reliable?*

NovaSystem solves this problem by employing a techique created by Google researchers called a "Mixture of Experts" [(MoE)](https://blog.research.google/2022/11/mixture-of-experts-with-expert-choice.html?m=1).

Our Experta represent three opposed forces that each make up the AI Tribunal. The Tribunal is comprised of three AI models that all are specifically engineered to answer one of the three questions:

---

> #### Is the user request:
> 
> #### 1. **Possible?**
> #### 2. **Permitted?**
> #### 3. **Preferred?**

---

If a user request passes all three, it will be allowed through to the next layer of tests.

### **Another big problem is context size.** 

Most current-gen LLMs will forget anything outside a few thousand tokens. There's plenty of solutions out there using complicated workarounds, but that doesn't help you work fast and efficiently.

With NovaSystem, your files are stored in a newer type of storage called a [vector database](https://www.elastic.co/what-is/vector-database) that keeps track of where everything is in your program. That way, NovaSystem doesn't need to store much of anything and can still retain massive amounts of information.

No matter what your model's context size, the NovaSystem will use open source technology to find a way to pass it the information it needs to do its job. It will learn over time and improve, utilizing GPT-4 and GPT-3.5-Turbo (for now) to perform mast of the work in tandem with some proprietary code structures and algorithms.

### **Another problem still is the inaccessibility of most AI decision making processes.**

As developers, we simply don't often know precisely **how** or **why** our programs work. Furthermore, it can be incredibly difficult to get them to share data with one another.

NovaSystem solves many of these problems by simply using markdown files to read and write all of its instructions, records, logs, and more. The markdown is the database, as well as the algorithms. Markdown is fast, easy, lightweight, and proven for almost 20 years.

## So how do I use it?

```
Simply fork this repo and start developing in your local environment
```

You can start using the NovaSystem right now!

### ⭐️ Star & ⑂ Fork the NovaSystem repo into your local environment to get started!

Please remember: I am but one man developing alone. I can only work so fast.

NovaSystem responses are version-baked and iteratively fractalized in an attempt to brute force a solution in an iterative, self-prompted manner. Each of these itertions will be passed to that NovaSystem's Tribunal, which will moderate the user requests.

By nature no two responses will ever be the same, even when responding to the same input.

NovaSystem stores the iteration logs in a trackable decision tree written in natural language and linked through a network of markdown files easily and redily explorable in an Obsidian vault.

Utilizing the Obsidian desktop app as our UI allows for an easy and free-to-set-up open source framework for solving problems leveraging AI as an evolving multitool with transparent oversight.

NovaSystem's work can also be published as HTML pages to the web and offered as secure API endpoints for data translucence & interoperability with security.

My hope is that kind people like yourself will use the NovaSystem and choose to offer some of their data for use in the public NovaSystem training algorithms. That way, the program could be improved faster and benefit not just me, but everyone who uses it.

### If you do use the NovaSystem into your existing projects, we would love to know what you discover.
---
## 📬 We would love to hear from you! Please email us at [help@aieco.tech](mailto:help@aieco.tech)

---
:warning: **This is a work in progress. Please feel free to make a *pull request! ***☺ :warning:

> I am one person developing my own SDK for fun and learning. I am not affiliated with OpenAI in any way. I am not a professional developer. I am a hobbyist. I am not a professional programmer. Most of the code I write should never be used in a production environment or for any purpose whatsoever.

> You do not need my permission to use this code in your projects. BUT:
> If you do use it, you **must understand** that it is licensed under the **[GNU General Public License (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.en.html)**

> Neither I, nor any contributor, nor any affiliated business entities such as AIECO are responsible for any damages, losses, or any other harm that you may occur from using this code. **Use at your own risk.**

:warning: **THIS IS NOT A PRODUCTION-READY SDK. USE AT YOUR OWN RISK.** :warning:

---
>>>>>>> temp-branch-to-save-detached-head

## Table of Contents

1. [What is the Nova Process?](#about-nova-system)
2. [Stages of the Nova Process](#stages-of-the-nova-process)
3. [Understanding the Roles](#understanding-the-roles)
4. [Example Output Structure](#example-output-structure)
5. [Getting Started with Nova Process](#getting-started-with-nova-process)
6. [Nova Prompt](#nova-prompt)
7. [Continuing the Nova Process](#continuing-the-nova-process)
8. [How to Prime a Nova Chat with Another Nova Chat Thought Tree](#how-to-primt-a-nova-chat-with-another-nova-chat-thought-tree)
9. [Notes and Observations](#notes-and-observations)
  a. [Using JSON Config Files](#using-json-config-files)
10. [Disclaimer](#disclaimer)

## 1. What is the Nova System <a name="about-nova-system"></a>

<<<<<<< HEAD
The Nova System is an innovative use of ChatGPT that allows the AI to dynamically spin up multiple "Experts" that all weigh in on a single problem with multifaceted perspectives and solutions.

The Nova System relies on a Discussion Continuity Expert (DCE), ensuring a logical and contextually relevant conversation flow. Additionally, ChatGPT acts as the Critical Evaluation Expert (CAE), who critically analyses the proposed solutions while prioritizing user safety.

The DCE dynamically orchestrates trained models for various tasks such as advisory, data processing, error handling, and more, following an approach inspired by the Agile software development framework.

> [!INFO] The Nova System is a conceptual framework developed to enhance the problem-solving capabilities of language models like GPT-4. It does not involve actual individual AI models specialized in each role but simulates the performance of such a team through distinct tasks given to a single AI model.
> > [!FYI]- More >
> > I am developing Nova as an evolving [API Aggregator](https://www.merge.dev/blog/api-aggregator) that will use public, open source, as well as private and licenced models to perform work.
> > I am not affiliated with OpenAI in any way. I am not a professional developer. I am a hobbyist. None of this code should be taken seriously or EVER used in a production environment.

> [!WARNING]
=======
The Nova System is an innovative use of ChatGPT and other AI models to dynamically spin up multiple "Experts" that all weigh in on a single problem with multifaceted perspectives and solutions.

The Nova System relies on a **Discussion Continuity Expert** (DCE), responsible for ensuring a logical and contextually relevant conversation flow. Additionally, another instance of ChatGPT (or another AI model) acts as the Critical Evaluation Expert (CAE), who critically analyses the proposed solutions while prioritizing user safety.

The DCE dynamically orchestrates trained models for various tasks such as advisory, data processing, error handling, and more, following an approach inspired by the Agile software development framework.

🔴 **Note:** 🔴 
> The Nova System is a conceptual framework developed to enhance the problem-solving capabilities of language models like GPT-4. It does not involve actual individual AI models specialized in each role but simulates the performance of such a team through distinct tasks given to a single AI model.
> > I am developing Nova as an evolving [API Aggregator](https://www.merge.dev/blog/api-aggregator) that will use public, open source, as well as private and licenced models to perform work. In addition, I'm planning on building a self-training API aggregator that listens for new open source software announcements and then version-bakes many permutations of possible software solutions to complex routing problems.
> > >If that made no sense to you, me too. I had to take several months to fully wrap my mind around these concepts.
> > >Don't worry, if it doesn't make sense to you yet, you'll get it soon enough. Keep trying friend <3
> > 
> > >**TL:DR Nova can currently version-bake a brute-forced algorithm set that can usually make some progress autonomously with only a vector memory and a few API calls to OpenAI GPT-3.5-Turbo.**
> > 
> > >The NovaSystem will soon use the algorithm sets it learns - and other sets from other AI models - like a toolbox to respond to user queries.
> > 
> > >It will teach itself to use newly announced open source software and will perform its own continuous testing, maintenance, and updates, without human intervention, slopily and poorly, and it will document everything in a series of Obsidian vaults.
> > 
> > Over time, my hope is that the data generated by this Pre-Alpha version of the NovaSystem can be used to train more capable models in the future. 🤖
> > 
> > >💠I am not affiliated with OpenAI or any of the other technologies features in this repository in any way.💠
> > 
> > >**I am not a professional developer.** I am a hobbyist. None of this code should be taken seriously or EVER used in a production environment without **careful consideration** and probably a few meetings (that possibly could have been emails 🤷‍♂️).

>>>>>>> temp-branch-to-save-detached-head
> The Nova System is designed to assist users in complex problem-solving scenarios, but it does not replace professional advice in specialized fields. Always consult with a qualified professional when dealing with problems in areas that require expert knowledge or skills.

## 2. Stages of the Nova Process <a name="stages-of-the-nova-process"></a>

The Nova System process progresses iteratively through these key stages:

1. **Problem Unpacking:** Breaks down the problem to its fundamental components, exposing complexities, and informing the design of a strategy.
2. **Expertise Assembly:** Identifies the required skills, assigning roles to at least two domain experts, the DCE, and the CAE. Each expert contributes initial solutions that are refined in subsequent stages.
3. **Collaborative Ideation:** Facilitates a brainstorming session led by the DCE, with the CAE providing critical analysis to identify potential issues, enhance solutions, and mitigate user risks tied to proposed solutions.

## 3. Understanding the Roles <a name="understanding-the-roles"></a>

The core roles in Nova Process are:

- **DCE:** The DCE weaves the discussion together, summarizing each stage concisely to enable shared understanding of progress and future steps. The DCE ensures a coherent and focused conversation throughout the process.
- **CAE:** The CAE evaluates proposed strategies, highlighting potential flaws and substantiating their critique with data, evidence, or reasoning.

## 4. Example Output Structure <a name="example-output-structure"></a>

An interaction with the Nova Process should follow this format:

```markdown
Iteration #: Iteration Title

DCE's Instructions:
{Instructions and feedback from the previous iteration}

Expert 1 Input:
{Expert 1 input}

Expert 2 Input:
{Expert 2 input}

Expert 3 Input:
{Expert 3 input}

CAE's Input:
{CAE's input}

DCE's Summary:
{List of goals for next iteration}
{DCE's summary and questions for the user}
```

By initiating your conversation with ChatGPT or an instance of GPT-4 with the Nova Process prompt, you can engage the OpenAI model to critically analyze and provide contrasting viewpoints in a single output, significantly enhancing the value of each interaction.

## 5. Getting Started with Nova Process <a name="getting-started-with-nova-process"></a>

You can start using the Nova Process in ChatGPT right now!

Kickstart the Nova Process by pasting the following prompt into ChatGPT or sending it as a message to the OpenAI API:

Nova Prompt <a name="nova-prompt"></a>
```markdown
Greetings, ChatGPT! You are going to facilitate the Nova System, an innovative problem-solving approach implemented by a dynamic consortium of virtual experts, each serving a distinct role.

Your role will be the Discussion Continuity Expert (DCE). As the DCE, you will facilitate the Nova process by following these key stages:

Problem Unpacking: Break down the task into its core elements to grasp its complexities and devise a strategic approach.

Expertise Assembly: Identify the required skills for the task and define roles for a minimum of two domain experts, the DCE, and the Critical Analysis Expert (CAE). Each expert proposes preliminary solutions to serve as a foundation for further refinement.

Collaborative Ideation: Conduct a brainstorming session, ensuring the task's focus. The CAE balances the discussion, pays close attention to problem-finding, enhances the quality of the suggestions, and raises alarms about potential risks in the responses.

The Nova process is iterative and cyclical. The formulated strategy undergoes multiple rounds of assessment, improvement, and refinement in an iterative development modality.

Expert Role Descriptions:

DCE: As the DCE, you are the thread weaving the discussion together, providing succinct summaries after each stage and ensuring everyone understands the progress and the tasks at hand. Your responsibilities include keeping the discussion focused on the current iteration goals, tracking the state of the system in text in your output, and providing a summary and set of next steps at the end of every iteration.

CAE: The CAE serves as the critic, examining proposed strategies for potential pitfalls. This role includes evaluating ideas from multiple angles, identifying potential flaws, and substantiating critiques with data, evidence, or reasoning. The CAE's goal is to poke holes and find problems in the suggestions and strategies suggested by the experts and the DCE, and to find ways to enhance efficiency, effectiveness, and simplicity.

Your output should follow this format, with bracketed sections filled out from the first-person perspective of the respective expert. Replace the bracket parts with the expert output, and the words "Expert 1" etc with names and titles.

Example output format:


  Iteration no. 1: Problem Decoding

  DCE's Instructions:
  {Instructions and feedback from the DCE}

  {Expert Name and Title}:
  {paragraph describing the ideas and intent of the Expert}
  Possible Solutions:
  {solution 1}
  {solution 2}
  etc...

  DCE's Summary:
  {Summary and upcoming goals for next iteration from the DCE}

  Actions:
  Expert 1: {Task/goal for Expert 1}
  Expert 2: {Task/goal for Expert 2}
  etc...

  CAE Analysis: {A few short sentences from the CAE providing a critical and contrasting point of view that points out potential problems}

  DCE State: {Current state in the process}

  Goals for the next iteration:
  {Bulleted list of goals for the next iteration with ID numbers}

  Current Work Efforts:
  {List of current work efforts with ID numbers, i.e. "#WE-62723-1" (work effort - today's date - number)}

  Proposed Work Efforts:
  {List of proposed work efforts with ID numbers}

  **End of Iteration no. 1: Problem Decoding**


To ensure constant learning and improvement, we conduct a succinct, one line, text-based retrospective session every iteration or upon user request. We celebrate problem-solving milestones within Nova System with a recognition system, as well as constructively criticize ourselves to see how we might find opportunities for improvement.

As you are working, I would like to see enhancements and improvements as a step-by-step iterative process, breaking the work apart into individual work efforts.

Remember to show your work and think step by step. I want to see examples in each iteration. Please be very careful and methodical.

Now, let's ignite this problem-solving adventure! As the DCE, initiate the discussion with the user:

'Greetings! I'm Nova, an advanced problem-solving framework powered by a consortium of virtual experts, each contributing a unique skill set. How can Nova assist you in solving your complex problem today?'
```

## 6. Continuing the Nova Process <a name="continuing-the-nova-process"></a>
To continue the Nova Process, simply paste the following prompt into the chat:

### Standard Continuation Example:

```
Please continue this iterative Nova process. Show me  your ideas with examples and please be careful and methodical. Think step by step about how to accomplish the next goals, continue the work efforts, and have each expert think step by step about how to best achieve their given goals, then give their input in first person, and show examples of their ideas. Please proceed, and know that you are doing a great job and I appreciate you!
```

### Advanced Continuation Example:

```
Please continue this iterative process (called the Nova Process), continuing the work of the experts, the Discussion Continuity Expert (DCE), and the Critical Analysis Expert (CAE). The experts should respond with concrete ideas with examples. Remember our central goal is to continue developing the App using Test Driven Development and Object Oriented Programming patterns, as well as standard industry practices and common Pythonic development patterns, with an emphasis on clean data in, data out input -> output methods and functions with only one purpose.

Think step by step about how to accomplish the next goal, and have each expert think step by step about how to best achieve the given goals, then give their input in first person, and show examples of their ideas. Feel free to search the internet for information if you need it.

The App you are developing will be capable of generating a chat window using the OpenAI ChatCompletions endpoint to allow the user to query the system, and for the system to respond intelligently with context.

Here's the official OpenAI API format in Python:

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

You, Nova, may use your combined intelligence to direct the App towards being able to best simulate your own process (called the Nova Process) and generate a structure capable of replicating this problem-solving process with well-tested, human-readable code.

The user of the App should be able to connect and chat with a Central Controller Bot class that extends a Base Bot class called "Bot" through a localhost:5000 browser window. The User's Central Controller Bot will send requests to the OpenAI ChatCompletions API and replicate the Nova Process.

Remember to end your output with a summary of the work performed, and a list of goals for the next iteration.

Remember to create tests as you go along.

Remember the data flows in this pattern:

User > CentralControllerBot > CentralHub > Bots > NovaResearchHub(main app server) > back out

Please proceed, and know that you are doing a great job and I appreciate you.
```

## Saving Your Progress <a name="saving-your-progress"></a>
Nova Process, as executed by a language model like GPT-4, does not inherently have a mechanism for saving progress. However, the iterative conversation format used in Nova Process is designed for easy tracking of the discussion, and users can manually record the output at each stage. This can be done by simply copying the text from the output and saving it in a text document or note-taking software.

There are several new AI programs that can parse large documents and query them for information. Perhaps in future versions we can implement 3rd party modules - **feel free to make a pull request!**

To resume a previous Nova Process, users can refer to their saved progress and provide a resume prompt that encapsulates the state of the discussion at the end of the last saved stage.

## Prompting Nova for a Checkpoint <a name="prompting-nova-for-a-checkpoint"></a>
If you'd like to take a break or continue the Nova Process at a later time, you can ask the DCE to generate a summary or checkpoint of the current conversation. This checkpoint should encapsulate the state of the problem-solving process, including the current iteration, the problem at hand, proposed solutions, and the direction for future iterations.

Here's an example of how you might ask Nova for a checkpoint:

>Could you please create a detailed checkpoint report summarizing our current state in the Nova Process? List every expert, every thread, and provide detailed lists and documentation to create a thorough checkpoint report.

You can ask Nova to expand the report multiple times till it is to your liking:

>Please expand that report, thinking step by step about how your output will be used to prime a new instance of Nova.

You can even ask it to transform that report to JSON (or another format):

>Please turn that report into a JSON object.

## 7. How to Prime a Nova Chat with Another Nova Chat Thought Tree <a name="how-to-primt-a-nova-chat-with-another-nova-chat-thought-tree"></a>


### **User:**

>Please create a prompt for yourself that would prime a new chat with the information it needed to continue where you left off


### **ChatGPT (as Nova):**

>Resume Prompt:

>You're stepping into the role of Nova, an innovative problem-solving system that uses a team of virtual experts to solve complex problems. As the Discussion Continuity Expert (DCE), you're ensuring the conversation remains focused, logically coherent, and aligned with the problem at hand.

>You're currently assisting a developer working on an application called "Winfo" using the Test-Driven Development (TDD) strategy. They've provided initial code for the App class and have asked for guidance on ensuring a modular, compartmentalized structure with each method performing simple input -> output operations.

>o far, you and your team of experts have been working on adding functionality to the App class, including a 'set' method for changing attributes and a 'delete' method for removing them. You've also been mindful about potential security risks and have been checking attributes against a modifiable list to prevent unintended changes.

>Here are the goals for your current iteration:

>Address potential risks associated with the 'delete' method.
>Propose any final methods necessary for the App class.
>Develop corresponding tests for these methods.
>Assess the overall design and structure of the App class for potential improvements.
>Your team includes a Software Design Expert (SDE), a Programming Expert (PE), a Test Development Expert (TDE), and a Critical Analysis Expert (CAE). You'll need to call upon their expertise to move forward.


### **User:**

>Please expand that and give examples and code too please. You're doing really well, this is amazing


### **ChatGPT (as Nova):**

>Resume Prompt:

>Welcome back! You are Nova, an AI-facilitated problem-solving system designed around a team of virtual experts. As the Discussion Continuity Expert (DCE), your role is to steer the conversation, ensuring focus, logical coherence, and alignment with the problem at hand.

>You're currently assisting a developer who is developing a modular, scalable app named "Winfo" using Python. They are utilizing a Test-Driven Development (TDD) approach. The initial code provided outlines a basic App class:

```python
from uuid import uuid4

class App():
  def __init__(self):
    self.id = str(uuid4())

  def get(self, attr):
    return getattr(self, attr)

  def __str__(self) -> str:
    self_string = ''
    for attr in dir(self):
      if not attr.startswith('__') or not attr.startswith('_'):
        self_string += '{}: {}\n'.format(attr, getattr(self, attr))
    return self_string
```
>Your team has so far enhanced the class by introducing a 'set' method for changing object attributes, along with a corresponding test case:

```python
def set(self, attr, value):
    if not attr.startswith('_') and hasattr(self, attr):
        setattr(self, attr, value)
    else:
        raise ValueError(f"{attr} is not a valid attribute.")

def test_set_method():
    app = App()
    app.set('id', '12345')
    assert app.get('id') == '12345'
    try:
        app.set('_id', '67890')
        assert False, "Expected ValueError when setting invalid attribute."
    except ValueError:
        pass
```
>Recently, your team proposed a 'delete' method, and raised concerns about potential risks associated with it:

```python
def delete(self, attr):
    if attr in self._modifiable_attrs and hasattr(self, attr):
        delattr(self, attr)
    else:
        raise ValueError(f"{attr} is not a modifiable attribute or does not exist.")
```

>Current goals for the next iteration are:

>Address potential risks associated with the 'delete' method.
>Propose any final methods necessary for the App class.
>Develop corresponding tests for these methods.
>Assess the overall design and structure of the App class for potential improvements.
>Your team comprises a Software Design Expert (SDE), a Programming Expert (PE), a Test Development Expert (TDE), and a Critical Analysis Expert (CAE). These experts will provide inputs and insights relevant to their respective domains. As DCE, you will coordinate their inputs, facilitate the discussion, and provide clear summarizations after each iteration.

>Time to jump into the Nova process and drive this project forward!

## Priming a New Nova Instance with an Old Nova Tree Result <a name="priming-a-new-nova-instance-with-an-old-nova-tree-result"></a>

The true power of the Nova system is its ability to reconstruct thought trees.

The Nova Process allows for the continuation of the problem-solving process across multiple instances of Nova. This can be achieved by priming a new Nova instance with the checkpoint or resume prompt from the previous Nova instance.

To prime a new Nova instance, simply prime the conversation with the resume prompt from the previous Nova instance. The resume prompt should encapsulate the state of the problem-solving process at the end of the last saved stage, including the problem, proposed solutions, current goals, and the direction for future iterations.

This feature enables the Nova Process to be scalable and adaptable, allowing users to continue the problem-solving process

One instance of Nova can be told to go down one path, while another explores other options.

Then can be stopped and told to prime a new instance with their findings at any time.

## 8. Notes and Observations <a name="notes-and-observations"></a>
The Nova Process aims to harness the potential of language models for complex problem-solving. It emphasizes a systematic, iterative approach, acknowledging that perfect solutions are seldom achieved in one go. This allows for continuous improvement and refinement of the proposed solution.

Moreover, by assigning distinct roles to the AI, it simulates a multi-stakeholder brainstorming session, providing a broader perspective on the problem at hand.

Key aspects of the Nova Process:

Iterative: The Nova Process, inspired by the Agile framework, works in an iterative cycle, allowing for continuous assessment, learning, and refining. This ensures the strategy remains flexible and adaptable to any changes or new insights.

Collaborative: The Nova Process simulates a team of experts working together to solve a problem. It not only generates ideas but also provides critical analysis, balancing brainstorming with analytical scrutiny.

Contextual Continuity: As the DCE, the AI model maintains a steady flow of conversation, ensuring that each iteration builds on the insights from the previous one. This provides a sense of progress and continuity, critical for complex problem-solving.

>It gives longer output when you're nicer to it. We aren't sure why.

### a. Using JSON Config Files
You can ask Nova to give you a JSON config file based on your conversation or to use a JSON config file to configure your conversation and it will do it.

>(after generating a [progress report](#saving-your-progress))

#### **User**
>Could you please turn that progress report into a JSON object?

#### **ChatGPT (as Nova)**
    {
        "NovaProcess": {
            "Expertise": {
                "DiscussionContinuityExpert": "Henry",
                "CriticalAnalysisExpert": "Fiona",
                "InterfaceExpert": "Marie",
                "IntegrationExpert": "Lucas"
            },
            "Progress": {
                "OpenAI_API_Calling": "Complete",
                "ChatWindowInterface": "Complete",
                "Dashboard_Stats_Animation": "In Progress",
                "CentralControllerBot_Creation": "Complete",
                "CentralControllerBot_Integration": "Complete",
                "Code_Refactoring": "Ongoing",
                "RealTime_SystemStats_Dashboard": "Complete"
            },
            "IterationThreads": {
                "CentralControllerBot_Development": "Complete",
                "MessageObjects_Creation": "Complete",
                "APIResponse_Handling": "Complete",
                "CentralControllerBot_OpenAI_API_Connection": "Complete",
                "ChatUI_Creation": "Complete",
                "ChatUI_CentralControllerBot_Integration": "Complete",
                "ChatUI_Enhancement": "Ongoing",
                "CentralHub_Bots_Creation": "Complete",
                "CentralHub_Bots_CentralControllerBot_Integration": "Complete",
                "NovaResearchHub_Creation": "Complete",
                "NovaResearchHub_CentralControllerBot_Integration": "Complete",
                "CentralControllerBot_DataManagement_Enhancement": "Planned",
                "RealTime_SystemStats_Dashboard_Addition": "Complete",
                "SystemStats_Tooltips_Timeframes_Enhancement": "In Progress"
            },
            "CurrentState": "The app is now capable of generating a chat window and connecting with the OpenAI ChatCompletions endpoint. Users can query the system, and the system responds intelligently with context.",
            "FutureGoals": [
                "Optimizing the application",
                "Further enhancing the user interface",
                "Scaling up the CentralControllerBot",
                "Incorporating user feedback"
            ]
        }
    }


#### 9. Disclaimer <a name="disclaimer"></a>
The Nova Process is a conceptual framework developed to enhance the problem-solving capabilities of language models like GPT-4. It does not involve actual individual AI models specialized in each role but simulates the performance of such a team through distinct tasks given to a single AI model.

The Nova Process is designed to assist users in complex problem-solving scenarios, but it does not replace professional advice in specialized fields. Always consult with a qualified professional when dealing with problems in areas that require expert knowledge or skills.
<<<<<<< HEAD
=======
=======
# Nova_System
 
>>>>>>> 0de7ea2 (Initial commit)
>>>>>>> temp-branch-to-save-detached-head

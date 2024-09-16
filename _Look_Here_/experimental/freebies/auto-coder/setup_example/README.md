# Auto Coder Setup

The `setup.js` script is designed to automate the initial setup process for the `auto-coder` tool, including installing necessary dependencies and downloading the main `auto-coder.js` script from the [NovaSystem](https://github.com/ctavolazzi/NovaSystem) repository.

## Prerequisites

Before running the setup script, ensure you have the following installed on your local machine:

1. **Ollama**: Make sure [Ollama](https://ollama.com/) is up and running on your local machine.
2. **Node.js**: Install Node.js from [nodejs.org](https://nodejs.org/).

## Setup Instructions

Follow these steps to set up the `auto-coder` tool:

1. **Create a New Directory**

   Create a new directory where you want to set up the `auto-coder` tool.

   ```bash
   mkdir auto-coder-setup
   cd auto-coder-setup
   ```

2. **Install the Required Package**

   Install the `@langchain/community` package by running the following command:

   ```bash
   npm install @langchain/community
   ```

3. **Add the `setup.js` Script**

   Download or copy the `setup.js` script into the directory. The `setup.js` script will handle the initial setup process, including creating necessary files and downloading the main `auto-coder.js` script.

4. **Run the Setup Script**

   Execute the `setup.js` script to install the necessary dependencies and set up the project:

   ```bash
   node setup.js
   ```

   The `setup.js` script will perform the following actions:
   - Create or update the `package.json` file to include the necessary dependencies and set the type to "module".
   - Install the required packages.
   - Create an `example_code.txt` file with default content if it doesn't exist.
   - Create a `config.json` file with default configuration values if it doesn't exist.
   - Download the main `auto-coder.js` script from the GitHub repository.

## Running the Auto Coder

Once `setup.js` is run, you can start the `auto-coder` by executing:

```bash
node auto-coder.js
```

## License

This project is licensed under the GPL-3.0 License.

## Contributing

If you have any suggestions, bug reports, or contributions, feel free to open an issue or submit a pull request. Your feedback and contributions are greatly appreciated!
```

This `README.md` provides clear instructions for setting up and running the `auto-coder` tool, as well as information about the prerequisites needed for the setup process.
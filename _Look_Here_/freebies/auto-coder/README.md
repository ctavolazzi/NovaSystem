# Auto Coder

The `auto-coder` tool is designed to automate code generation and improvement processes using the `Ollama` model from the `@langchain/community` package. This tool can help streamline your coding tasks by generating and refining code based on specified parameters.

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

   Execute the `setup.js` script to complete the setup process:

   ```bash
   node setup.js
   ```

   The `setup.js` script will perform the following actions:
   - Create or update the `package.json` file to include the necessary dependencies and set the type to "module".
   - Install the required packages.
   - Create an `example_code.txt` file with default content if it doesn't exist.
   - Create a `config.json` file with default configuration values if it doesn't exist.
   - Download the main `auto-coder.js` script from the GitHub repository.

5. **Run the `auto-coder.js` Script**

   After the setup is complete, you can run the `auto-coder.js` script to start using the tool:

   ```bash
   node auto-coder.js
   ```

## License

This project is licensed under the GPL-3.0 License.

## Contributing

If you have any suggestions, bug reports, or contributions, feel free to open an issue or submit a pull request. Your feedback and contributions are greatly appreciated!
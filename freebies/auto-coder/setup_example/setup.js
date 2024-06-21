import fs from 'fs/promises';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';
import https from 'https';

const execAsync = promisify(exec);

async function installPackages() {
  try {
    console.log('Installing packages...');
    const { stdout, stderr } = await execAsync('npm install @langchain/community');
    if (stderr) {
      console.error(`Error installing packages: ${stderr}`);
      return;
    }
    console.log(`Packages installed successfully:\n${stdout}`);
  } catch (error) {
    console.error(`Error installing packages: ${error.message}`);
  }
}

async function createExampleCodeFile() {
  const filePath = path.join(process.cwd(), 'example_code.txt');
  const defaultContent = 'This is the default content of example_code.txt';

  try {
    await fs.access(filePath);
    console.log(`File already exists: ${filePath}`);
  } catch (error) {
    console.log(`Creating file: ${filePath}`);
    await fs.writeFile(filePath, defaultContent, 'utf8');
    console.log(`File created successfully with default content: ${filePath}`);
  }
}

async function createConfigFile() {
  const configPath = path.join(process.cwd(), 'config.json');
  const defaultConfig = {
    language: "JavaScript",
    functionality: "example functionality",
    exampleCodePath: path.join(process.cwd(), 'example_code.txt'),
    iterations: 5,
    codeIntention: "Create a sample function",
    focusArea: "Initial focus on code structure and functionality",
    nextSteps: "Begin by implementing basic functionality and ensuring code structure is sound."
  };

  try {
    await fs.access(configPath);
    console.log(`Config file already exists: ${configPath}`);
  } catch (error) {
    console.log(`Creating config file: ${configPath}`);
    await fs.writeFile(configPath, JSON.stringify(defaultConfig, null, 2), 'utf8');
    console.log(`Config file created successfully: ${configPath}`);
  }
}

async function downloadFile(url, dest) {
  const file = fs.createWriteStream(dest);
  return new Promise((resolve, reject) => {
    https.get(url, (response) => {
      response.pipe(file);
      file.on('finish', () => {
        file.close(resolve);
      });
    }).on('error', (err) => {
      fs.unlink(dest);
      reject(err.message);
    });
  });
}

async function downloadAutoMainScript() {
  const url = 'https://raw.githubusercontent.com/your-repo-path/auto-main.js'; // Replace with the actual URL
  const dest = path.join(process.cwd(), 'auto-main.js');

  try {
    await downloadFile(url, dest);
    console.log('auto-main.js downloaded successfully.');
  } catch (error) {
    console.error(`Error downloading auto-main.js: ${error}`);
  }
}

async function setup() {
  await installPackages();
  await createExampleCodeFile();
  await createConfigFile();
  await downloadAutoMainScript();
  console.log('Setup completed successfully.');
}

setup();

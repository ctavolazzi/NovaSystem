const fs = require('fs');
const fsp = require('fs/promises');
const path = require('path');
const { exec } = require('child_process');
const https = require('https');
const { promisify } = require('util');

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
    await fsp.access(filePath);
    console.log(`File already exists: ${filePath}`);
  } catch (error) {
    console.log(`Creating file: ${filePath}`);
    await fsp.writeFile(filePath, defaultContent, 'utf8');
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
    await fsp.access(configPath);
    console.log(`Config file already exists: ${configPath}`);
  } catch (error) {
    console.log(`Creating config file: ${configPath}`);
    await fsp.writeFile(configPath, JSON.stringify(defaultConfig, null, 2), 'utf8');
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
  const url = 'https://raw.githubusercontent.com/ctavolazzi/NovaSystem/main/freebies/auto-coder/auto-coder.js';
  const dest = path.join(process.cwd(), 'auto-coder.js');

  try {
    await downloadFile(url, dest);
    console.log('auto-coder.js downloaded successfully.');
  } catch (error) {
    console.error(`Error downloading auto-coder.js: ${error}`);
  }
}

async function createPackageJson() {
  const packageJsonPath = path.join(process.cwd(), 'package.json');
  let packageJson = {
    name: "setup_example",
    version: "1.0.0",
    type: "module",
    dependencies: {
      "@langchain/community": "^0.0.1"
    }
  };

  try {
    const existingPackageJson = JSON.parse(await fsp.readFile(packageJsonPath, 'utf8'));
    packageJson = {
      ...existingPackageJson,
      ...packageJson,
      dependencies: {
        ...existingPackageJson.dependencies,
        ...packageJson.dependencies
      }
    };
    console.log(`Updating existing package.json at ${packageJsonPath}`);
  } catch (error) {
    console.log(`Creating new package.json at ${packageJsonPath}`);
  }

  await fsp.writeFile(packageJsonPath, JSON.stringify(packageJson, null, 2), 'utf8');
  console.log(`package.json file created/updated successfully.`);
}

async function setup() {
  await createPackageJson();
  await installPackages();
  await createExampleCodeFile();
  await createConfigFile();
  await downloadAutoMainScript();
  console.log('Setup completed successfully.');
}

setup();

// auto-coder.js
// Chunk 1: Imports and Initial Setup
import { Ollama } from "@langchain/community/llms/ollama";
import { PromptTemplate } from "@langchain/core/prompts";
import fs from 'fs/promises';
import path from 'path';
import { performance } from 'perf_hooks';
import readline from 'readline';
import { v4 as uuidv4 } from 'uuid';

const llm = new Ollama({
  model: "codellama",
  baseUrl: "http://localhost:11434",
});

function generateUniqueId() {
    return uuidv4();
}

// Chunk 2: Prompt Templates
const codePrompt = PromptTemplate.fromTemplate(`
Code Intention: {codeIntention}
Code Intent Interpretation: {codeIntent}
Focus Area: {focusArea}

Write a function in {language} that {functionality}. The code should have the following characteristics:

- Clear and readable code
- Proper error handling
- Efficient implementation
- Well-documented with comments
- Special focus on {focusArea}

Here's an example of what the code might look like:

{exampleCode}

Now, please write a function in {language} that {functionality}, keeping in mind the desired characteristics, the example provided, the code intention, the interpreted code intent, and the specified focus area.
`);

const analysisPrompt = PromptTemplate.fromTemplate(`
Code Intention: {codeIntention}
Code Intent Interpretation: {codeIntent}
Focus Area: {focusArea}

Please analyze the following code:

{code}

Provide specific suggestions for improving the code in terms of:

1. Readability and clarity
2. Error handling
3. Efficiency and performance
4. Documentation and comments
5. Alignment with the code intention and interpreted code intent
6. Addressing the specified focus area: {focusArea}

Please offer specific examples and concrete revisions where applicable. The suggestions should be actionable and aimed at elevating the overall quality of the code and ensuring it meets the user's requirements.
`);

const improvementPrompt = PromptTemplate.fromTemplate(`
Code Intention: {codeIntention}
Code Intent Interpretation: {codeIntent}
Focus Area: {focusArea}

Here is the original code:

{code}

And here are the suggestions for improvement:

{suggestions}

Please revise the code, incorporating the provided suggestions while maintaining the original functionality. Focus on enhancing the readability, error handling, efficiency, documentation, alignment with the code intention and interpreted code intent, and addressing the specified focus area.

Implement the suggestions directly into the code, making the necessary changes and refinements. The goal is to elevate the quality of the code based on the analysis and feedback provided and ensure it meets the user's requirements.

Please present the revised code, showcasing the improvements made.
`);

const intentCheckPrompt = PromptTemplate.fromTemplate(`
Code Intention: {codeIntention}
Code Intent Interpretation: {codeIntent}
Focus Area: {focusArea}

Here is the latest version of the code:

{code}

Please answer the following questions:

1. Does this new code match the code intent?
2. Is it fully expressing the nature of what was asked for in the code intention?
3. Does it adequately address the specified focus area?
4. Is there more room for improvement and better alignment with the code intent and focus area?

Provide detailed feedback on each question and suggest specific improvements if necessary.
`);

const discrepancyCheckPrompt = PromptTemplate.fromTemplate(`
Original example code:
{exampleCode}

Generated code:
{generatedCode}

Focus Area: {focusArea}

Please analyze the two code snippets above and answer the following questions:

1. Are there any major discrepancies between the original example code and the generated code?
2. If there are discrepancies, what are they?
3. How can the generated code be improved to better align with the original example code?
4. Does the generated code adequately address the specified focus area?

Provide a detailed analysis and specific suggestions for improvement.
`);

// Chunk 3: Utility Functions
function getUserInput(question) {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  
    return new Promise((resolve) => {
      rl.question(question, (answer) => {
        rl.close();
        resolve(answer);
      });
    });
}

async function interpretUserIntent(codeIntention, focusArea) {
    const intentPrompt = PromptTemplate.fromTemplate(`
      Please interpret the user's intent from the following input and focus area:
  
      Code Intention: {codeIntention}
      Focus Area: {focusArea}
  
      Provide a concise interpretation of what the user is asking for, including:
      - The main goal or functionality
      - Any specific features or requirements
      - The programming language (if specified)
      - Any constraints or additional context
      - How the focus area should be incorporated into the code and its functionality
  
      Your interpretation should explicitly address how the focus area affects the overall intent and desired outcome.

      Your interpretation:
    `);
  
    const prompt = await intentPrompt.format({ codeIntention, focusArea });
    return await llm.invoke(prompt);
}

async function generateCode(language, functionality, exampleCode, codeIntention, codeIntent, focusArea) {
  const prompt = await codePrompt.format({ language, functionality, exampleCode, codeIntention, codeIntent, focusArea });
  return await llm.invoke(prompt);
}

async function analyzeCode(code, codeIntention, codeIntent, focusArea) {
  const prompt = await analysisPrompt.format({ code, codeIntention, codeIntent, focusArea });
  return await llm.invoke(prompt);
}

async function improveCode(code, suggestions, codeIntention, codeIntent, focusArea) {
  const prompt = await improvementPrompt.format({ code, suggestions, codeIntention, codeIntent, focusArea });
  return await llm.invoke(prompt);
}

async function checkUserIntentAlignment(code, codeIntention, codeIntent, focusArea) {
  const prompt = await intentCheckPrompt.format({ code, codeIntention, codeIntent, focusArea });
  return await llm.invoke(prompt);
}

async function checkForDiscrepancies(exampleCode, generatedCode, focusArea) {
  const prompt = await discrepancyCheckPrompt.format({ exampleCode, generatedCode, focusArea });
  return await llm.invoke(prompt);
}

async function compareCode(newCode, bestCode, previousCode, focusArea) {
  const comparePrompt = `
    Compare the following code snippets:

    New Code:
    ${newCode}

    Best Code:
    ${bestCode}

    Previous Code:
    ${previousCode}

    Focus Area: ${focusArea}

    Provide a detailed analysis of the improvements made in the new code compared to the best code and previous code. Consider factors such as readability, error handling, efficiency, documentation, alignment with the user's requirements, and how well it addresses the focus area.

    Indicate which code version is the best overall and explain why.
  `;
  const comparisonResult = await llm.invoke(comparePrompt);
  return comparisonResult.trim();
}

async function generateAggregateCode(cleanBestCode, cleanInitialCode, goodEnoughCode) {
    const aggregatePrompt = `
        Compare and analyze the following code versions:

        Clean Best Code:
        ${cleanBestCode}

        Clean Initial Code:
        ${cleanInitialCode}

        Good Enough Code:
        ${goodEnoughCode}

        Based on these code versions, generate a final, optimized version that combines the best aspects of each. 
        Consider readability, efficiency, error handling, and overall code quality.
        Provide a brief explanation of the choices made in creating this aggregate version.

        Aggregate Code:
    `;

    const aggregateResult = await llm.invoke(aggregatePrompt);
    return aggregateResult.trim();
}

// Chunk 4: Code Evaluation and Cleaning Functions
async function evaluateCodeFitness(code, codeIntention, codeIntent, focusArea, iterationDir) {
    const evaluationPrompt = `
      Given the following code:
      ${code}
  
      And the code intention:
      ${codeIntention}
  
      And the interpreted code intent:
      ${codeIntent}
  
      And the focus area:
      ${focusArea}
  
      Please evaluate if the code meets the user's requirements and aligns with their intent. Consider the following criteria:
      - Functionality: Does the code fulfill the desired functionality based on the code intention?
      - Readability: Is the code easy to understand and follow?
      - Error Handling: Does the code properly handle potential errors?
      - Efficiency: Is the code efficient in terms of performance?
      - Documentation: Is the code well-documented with comments?
      - Alignment: Is the code consistent with the interpreted code intent?
      - Focus Area: Does the code adequately address the specified focus area?
  
      Provide a detailed analysis of the code's fitness and indicate whether it successfully meets the user's requirements and intent. Explain your reasoning.
    `;
    const evaluationResult = await llm.invoke(evaluationPrompt);
    
    const fitnessPath = path.join(iterationDir, 'fitness_evaluation.txt');
    await fs.writeFile(fitnessPath, evaluationResult, 'utf8');
    
    const meetsRequirements = evaluationResult.toLowerCase().includes('meets the user\'s requirements');
    return meetsRequirements;
}

async function cleanCode(code) {
    const cleanPrompt = `
      Here is a code snippet that needs to be cleaned and formatted correctly:
  
      ${code}
  
      Output the code in a markdown formatted code block, and nothing else.
      Please correct any syntax errors, fix formatting issues, and ensure the code follows best practices and conventions. Return only the cleaned and formatted code. You must only return the code, and nothing else. Do not return any additional text or comments. Return ONLY the code and nothing else. DO NOT USE THE PHRASE: "Here is the cleaned and formatted code:" or "Here's the revised version of the code with the syntax errors fixed and formatting issues resolved:" or anything similar.
      Output only the code itself in its entirety, without any additional text or comments, and in a markdown formatted code block.
      `;
    const cleanedCode = await llm.invoke(cleanPrompt);
    return cleanedCode.trim();
}

// Chunk 5: File Operations and Iteration Setup
async function saveToFile(content, filePath, id = generateUniqueId()) {
    console.log(`Saving content to ${filePath} with ID: ${id}`);
    if (content === undefined) {
      console.warn(`Warning: Content is undefined. Skipping save to ${filePath}`);
      return;
    }
    if (typeof content !== 'string' && !(content instanceof Buffer)) {
      throw new TypeError('The "data" argument must be of type string or an instance of Buffer. Received ' + typeof content);
    }
    const contentWithId = `Document ID: ${id}\n\n${content}`;
    await fs.writeFile(filePath, contentWithId, 'utf8');
    console.log(`File saved to ${filePath}`);
    return id;
}

async function createIterationFolder(runDir, iteration) {
    const iterationDir = path.join(runDir, `iteration_${iteration}`);
    await fs.mkdir(iterationDir);
    return iterationDir;
}

async function saveExampleCode(code, filePath) {
    await fs.writeFile(filePath, code, 'utf8');
    console.log(`Example code saved to ${filePath}`);
}

async function saveAutoCode(code) {
    const autoCodePath = path.join(process.cwd(), 'auto_code.txt');
    const cleanedCode = await cleanCode(code);
    await fs.writeFile(autoCodePath, cleanedCode, 'utf8');
    console.log(`Auto code saved to: ${autoCodePath}`);
}

async function loadConfig(configPath) {
    const config = JSON.parse(await fs.readFile(configPath, 'utf8'));
    return config;
}

async function saveConfig(configPath, config) {
    await fs.writeFile(configPath, JSON.stringify(config, null, 2), 'utf8');
    console.log(`Config saved to ${configPath}`);
}

// Chunk 6: Main Code Improvement Function
async function runCodeImprovement(language, functionality, exampleCodePath, codeIntention, codeIntent, iterations, runDir, focusArea) {
    const receipt = {
      language,
      functionality,
      codeIntention,
      codeIntent,
      focusArea,
      iterations,
      startTime: new Date(),
      endTime: null,
      duration: null,
      initialCodePath: '',
      bestCodePath: '',
      goodEnoughCodePath: '',
      iterationDetails: [],
      documentIds: {
        initialCode: '',
        bestCode: '',
        goodEnoughCode: '',
      },
    };
  
    console.log(`\n--- Code Improvement Process ---`);
    console.log(`Language: ${language}`);
    console.log(`Functionality: ${functionality}`);
    console.log(`Code Intention: ${codeIntention}`);
    console.log(`Focus Area: ${focusArea}`);
    console.log(`Number of Iterations: ${iterations}`);
    console.log(`Run Directory: ${runDir}`);
    console.log(`Start Time: ${receipt.startTime.toLocaleString()}`);
    console.log(`----------------------------------`);
  
    const exampleCode = await fs.readFile(exampleCodePath, 'utf8');
    console.log(`Example code read from ${exampleCodePath}`);
  
    const codeIntentionPath = path.join(runDir, 'code_intention.txt');
    await saveToFile(codeIntention, codeIntentionPath);
  
    const codeIntentPath = path.join(runDir, 'code_intent.txt');
    await saveToFile(codeIntent, codeIntentPath);
  
    let initialCode = await generateCode(language, functionality, exampleCode, codeIntention, codeIntent, focusArea);
    const initialCodePath = path.join(runDir, 'initial_code.txt');
    receipt.documentIds.initialCode = await saveToFile(initialCode, initialCodePath);
    receipt.initialCodePath = initialCodePath;
  
    console.log(`\nInitial Code:`);
    console.log(`--------------`);
    console.log(initialCode);
    console.log(`Saved to: ${initialCodePath}`);
  
    let bestCode = initialCode;
    let previousCode = initialCode;
    let goodEnoughCode = null;
    let improvedCode = initialCode;

    for (let i = 1; i <= iterations; i++) {
        console.log(`\n--- Iteration ${i} ---`);
        const startTime = performance.now();

        const iterationDir = await createIterationFolder(runDir, i);
        let improvedCodeFilePath = path.join(iterationDir, 'improved_code.txt');
        let suggestionsPath = '';
        let iterationAnalysisPath = '';
        let discrepancyCheckPath = '';

        const meetsRequirements = await evaluateCodeFitness(improvedCode, codeIntention, codeIntent, focusArea, iterationDir);
        console.log(`\nCode Fitness Evaluation: ${meetsRequirements ? 'Pass' : 'Fail'}`);
  
        if (meetsRequirements && !goodEnoughCode) {
            goodEnoughCode = improvedCode;
            const goodEnoughCodePath = path.join(runDir, 'good_enough_code.txt');
            await saveToFile(goodEnoughCode, goodEnoughCodePath);
            receipt.goodEnoughCodePath = goodEnoughCodePath;
            console.log(`\nGood Enough Code saved to: ${goodEnoughCodePath}`);
        }
  
        console.log(`\nChecking User Intent Alignment...`);
        const intentCheckResult = await checkUserIntentAlignment(improvedCode, codeIntention, codeIntent, focusArea);
        console.log(`\nUser Intent Alignment Check:`);
        console.log(intentCheckResult);
  
        const suggestions = await analyzeCode(improvedCode, codeIntention, codeIntent, focusArea);
        suggestionsPath = path.join(iterationDir, 'suggestions.txt');
        await saveToFile(suggestions, suggestionsPath);
  
        const discrepancyCheck = await checkForDiscrepancies(exampleCode, improvedCode, focusArea);
        discrepancyCheckPath = path.join(iterationDir, 'discrepancy_check.txt');
        await saveToFile(discrepancyCheck, discrepancyCheckPath);
  
        improvedCode = await improveCode(improvedCode, suggestions + '\n' + discrepancyCheck, codeIntention, codeIntent, focusArea);
        await saveToFile(improvedCode, improvedCodeFilePath);

        console.log(`\nImproved Code:`);
        console.log(`--------------`);
        console.log(improvedCode);
        console.log(`Saved to: ${improvedCodeFilePath}`);

        const iterationAnalysis = await compareCode(improvedCode, bestCode, previousCode, focusArea);
        iterationAnalysisPath = path.join(iterationDir, 'iteration_analysis.txt');
        await saveToFile(iterationAnalysis, iterationAnalysisPath);

        console.log(`\nIteration Analysis:`);
        console.log(`-------------------`);
        console.log(iterationAnalysis);
        console.log(`Saved to: ${iterationAnalysisPath}`);

        bestCode = improvedCode;

        const cleanedImprovedCode = await cleanCode(improvedCode);
        const cleanedImprovedCodePath = path.join(iterationDir, 'cleaned_improved_code.txt');
        
        console.log(`\nCleaned Improved Code:`);
        console.log(`----------------------`);
        console.log(cleanedImprovedCode);
        console.log(`Saved to: ${cleanedImprovedCodePath}`);

        // Generate and save the aggregate code after each iteration
        const aggregateCode = await generateAggregateCode(cleanedImprovedCode, await cleanCode(initialCode), goodEnoughCode || cleanedImprovedCode);
        const aggregateCodePath = path.join(iterationDir, 'aggregate_code.txt');
        await saveToFile(aggregateCode, aggregateCodePath);

        console.log(`\nAggregate Code generated and saved to: ${aggregateCodePath}`);

        // Save the cleaned aggregate code as auto_code.txt
        await saveAutoCode(aggregateCode);

        const endTime = performance.now();
        const duration = (endTime - startTime) / 1000;

        console.log(`\nIteration Duration: ${duration.toFixed(2)} seconds`);

        const iterationDetail = {
            iteration: i,
            improvedCodePath: improvedCodeFilePath,
            cleanedImprovedCodePath,
            suggestionsPath,
            iterationAnalysisPath,
            aggregateCodePath,
            duration,
            documentIds: {
                improvedCode: await saveToFile(improvedCode, improvedCodeFilePath),
                cleanedImprovedCode: await saveToFile(cleanedImprovedCode, cleanedImprovedCodePath),
                suggestions: suggestionsPath ? await saveToFile(suggestions, suggestionsPath) : '',
                iterationAnalysis: iterationAnalysisPath ? await saveToFile(iterationAnalysis, iterationAnalysisPath) : '',
                discrepancyCheck: discrepancyCheckPath ? await saveToFile(discrepancyCheck, discrepancyCheckPath) : '',
                aggregateCode: await saveToFile(aggregateCode, aggregateCodePath),
            },
        };

        receipt.iterationDetails.push(iterationDetail);
        previousCode = improvedCode;
    }

    const bestCodePath = path.join(runDir, 'best_code.txt');
    await saveToFile(bestCode, bestCodePath);
    receipt.bestCodePath = bestCodePath;

    console.log(`\nBest Code (Final Iteration):`);
    console.log(`-----------------------------`);
    console.log(bestCode);
    console.log(`Saved to: ${bestCodePath}`);

    const cleanBestCode = await cleanCode(bestCode);
    const cleanBestCodePath = path.join(runDir, 'clean_best_code.txt');
    await saveToFile(cleanBestCode, cleanBestCodePath);

    const cleanInitialCode = await cleanCode(initialCode);
    const cleanInitialCodePath = path.join(runDir, 'clean_initial_code.txt');
    await saveToFile(cleanInitialCode, cleanInitialCodePath);

    // Generate final aggregate code
    const finalAggregateCode = await generateAggregateCode(cleanBestCode, cleanInitialCode, goodEnoughCode || cleanBestCode);
    const finalAggregateCodePath = path.join(runDir, 'final_aggregate_code.txt');
    await saveToFile(finalAggregateCode, finalAggregateCodePath);

    console.log(`\nFinal Aggregate Code generated and saved to: ${finalAggregateCodePath}`);

    // Save the final cleaned aggregate code as auto_code.txt
    await saveAutoCode(finalAggregateCode);

    receipt.endTime = new Date();
    receipt.duration = (receipt.endTime - receipt.startTime) / 1000;

    console.log(`\n--- Code Improvement Process Completed ---`);
    console.log(`End Time: ${receipt.endTime.toLocaleString()}`);
    console.log(`Total Duration: ${receipt.duration.toFixed(2)} seconds`);

    const receiptFileName = `run_receipt_${path.basename(runDir)}.txt`;
    const receiptPath = path.join(runDir, receiptFileName);
    const receiptContent = generateReceiptContent(receipt);
    await saveToFile(receiptContent, receiptPath);

    console.log(`\nRun Receipt:`);
    console.log(`------------`);
    console.log(receiptContent);
    console.log(`Saved to: ${receiptPath}`);

    const newExampleCodePath = path.join(process.cwd(), 'example_code.txt');
    await saveToFile(cleanBestCode, newExampleCodePath);

    return receipt;
}

// Chunk 7: Receipt Generation and Focus Area Functions
function generateReceiptContent(receipt) {
    let content = `Code Improvement Run Receipt\n`;
    content += `===========================\n\n`;
    content += `**Language:** ${receipt.language}\n`;
    content += `**Functionality:** ${receipt.functionality}\n`;
    content += `**Code Intention:** ${receipt.codeIntention}\n`;
    content += `**Focus Area:** ${receipt.focusArea}\n`;
    content += `**Number of Iterations:** ${receipt.iterations}\n`;
    content += `**Start Time:** ${receipt.startTime.toLocaleString()}\n`;
    content += `**End Time:** ${receipt.endTime.toLocaleString()}\n`;
    content += `**Total Duration:** ${receipt.duration.toFixed(2)} seconds\n\n`;
    content += `**Initial Code:** ${receipt.initialCodePath} (ID: ${receipt.documentIds.initialCode})\n`;
    content += `**Best Code:** ${receipt.bestCodePath} (ID: ${receipt.documentIds.bestCode})\n`;
    content += `**Good Enough Code:** ${receipt.goodEnoughCodePath} (ID: ${receipt.documentIds.goodEnoughCode})\n\n`;
    content += `## Iteration Details:\n`;

    for (const detail of receipt.iterationDetails) {
        content += `### Iteration ${detail.iteration}:\n`;
        content += `- **Improved Code:** ${detail.improvedCodePath} (ID: ${detail.documentIds.improvedCode})\n`;
        content += `- **Cleaned Improved Code:** ${detail.cleanedImprovedCodePath} (ID: ${detail.documentIds.cleanedImprovedCode})\n`;
        content += `- **Suggestions:** ${detail.suggestionsPath} (ID: ${detail.documentIds.suggestions})\n`;
        if (detail.documentIds.discrepancyCheck) {
            content += `- **Discrepancy Check:** ${detail.discrepancyCheckPath} (ID: ${detail.documentIds.discrepancyCheck})\n`;
        }
        content += `- **Iteration Analysis:** ${detail.iterationAnalysisPath} (ID: ${detail.documentIds.iterationAnalysis})\n`;
        content += `- **Aggregate Code:** ${detail.aggregateCodePath} (ID: ${detail.documentIds.aggregateCode})\n`;
        content += `- **Duration:** ${detail.duration.toFixed(2)} seconds\n\n`;
    }

    return content;
}

async function generateFocusArea(codeIntention, previousFocusArea, nextSteps) {
    const focusAreaPrompt = PromptTemplate.fromTemplate(`
      Based on the following information:

      Code Intention: {codeIntention}
      Previous Focus Area: {previousFocusArea}
      Next Steps: {nextSteps}

      Generate a new focus area for the next round of code improvement. The focus area should address the most critical aspects mentioned in the next steps while considering the overall code intention.

      New Focus Area:
    `);

    const prompt = await focusAreaPrompt.format({ codeIntention, previousFocusArea, nextSteps });
    return await llm.invoke(prompt);
}

async function evaluateNextSteps(bestCode, codeIntention, focusArea) {
    const nextStepsPrompt = PromptTemplate.fromTemplate(`
      Analyze the following code and provide next steps for further improvement:

      Code:
      {bestCode}

      Code Intention: {codeIntention}
      Current Focus Area: {focusArea}

      Evaluate the code and suggest specific next steps for improvement. Consider the following aspects:
      1. Code quality and best practices
      2. Efficiency and performance
      3. Readability and maintainability
      4. Alignment with the code intention
      5. Areas that weren't fully addressed in the current focus area

      If you believe the code has reached a satisfactory state and no further improvements are necessary, explicitly state that there are no more next steps.

      Next Steps:
    `);

    const prompt = await nextStepsPrompt.format({ bestCode, codeIntention, focusArea });
    return await llm.invoke(prompt);
}

// Chunk 8: Main Function
async function main() {
    const configPath = path.join(process.cwd(), 'config.json');
    let config = await loadConfig(configPath);
    let { language, functionality, exampleCodePath, iterations, codeIntention, focusArea, nextSteps } = config;

    if (!focusArea) {
        focusArea = "Initial focus on code structure and functionality";
    }
    if (!nextSteps) {
        nextSteps = "Begin by implementing basic functionality and ensuring code structure is sound.";
    }

    while (true) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const runName = `run_${timestamp}`;
        const runDir = path.join(process.cwd(), 'code-iterations', runName);
        await fs.mkdir(runDir, { recursive: true });

        console.log(`\nStarting new iteration with focus area: ${focusArea}`);
        console.log(`Next steps from previous iteration: ${nextSteps}`);

        const codeIntent = await interpretUserIntent(codeIntention, focusArea);
        if (codeIntent) {
            const codeIntentPath = path.join(runDir, 'code_intent.txt');
            await saveToFile(codeIntent, codeIntentPath);
            console.log("Code intent interpreted and saved.");
        } else {
            console.warn("Warning: Failed to interpret code intent. Proceeding without it.");
        }

        const receipt = await runCodeImprovement(language, functionality, exampleCodePath, codeIntention, codeIntent, iterations, runDir, focusArea);

        await saveExampleCode(await fs.readFile(receipt.bestCodePath, 'utf8'), exampleCodePath);

        const bestCode = await fs.readFile(receipt.bestCodePath, 'utf8');
        nextSteps = await evaluateNextSteps(bestCode, codeIntention, focusArea);
        const nextStepsPath = path.join(runDir, 'next_steps.txt');
        await saveToFile(nextSteps, nextStepsPath);

        console.log("\nNext steps:");
        console.log(nextSteps);

        if (nextSteps.toLowerCase().includes("no more next steps") || nextSteps.trim() === "") {
            console.log("No more improvements needed. Stopping the process.");
            break;
        }

        focusArea = await generateFocusArea(codeIntention, focusArea, nextSteps);
        console.log(`\nNew focus area for next iteration: ${focusArea}`);

        config.focusArea = focusArea;
        config.nextSteps = nextSteps;
        config.lastAggregateCodePath = path.join(runDir, 'final_aggregate_code.txt');
        await saveConfig(configPath, config);
        console.log("Config updated with new focus area, next steps, and last aggregate code path.");

        await new Promise(resolve => setTimeout(resolve, 5000));
    }

    console.log("Automated code improvement process completed.");
}

main();
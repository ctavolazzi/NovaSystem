// auto-writer.js
// Chunk 1: Imports and Initial Setup
import { Ollama } from "@langchain/community/llms/ollama";
import { PromptTemplate } from "@langchain/core/prompts";
import fs from 'fs/promises';
import path from 'path';
import { performance } from 'perf_hooks';
import readline from 'readline';
import { v4 as uuidv4 } from 'uuid';

const llm = new Ollama({
  model: "mistral", // or another suitable model for text generation
  baseUrl: "http://localhost:11434",
});

function generateUniqueId() {
    return uuidv4();
}

// Chunk 2: Prompt Templates
const documentPrompt = PromptTemplate.fromTemplate(`
Document Intention: {documentIntention}
Document Intent Interpretation: {documentIntent}
Focus Area: {focusArea}

Write a {documentType} about {topic}. The document should have the following characteristics:

- Clear and engaging content
- Proper structure and flow
- Efficient conveyance of information
- Well-formatted with appropriate headings and sections
- Special focus on {focusArea}

Here's an example of what the document structure might look like:

{exampleDocument}

Now, please write a {documentType} about {topic}, keeping in mind the desired characteristics, the example provided, the document intention, the interpreted document intent, and the specified focus area.
`);

const analysisPrompt = PromptTemplate.fromTemplate(`
Document Intention: {documentIntention}
Document Intent Interpretation: {documentIntent}
Focus Area: {focusArea}

Please analyze the following document:

{document}

Provide specific suggestions for improving the document in terms of:

1. Clarity and engagement
2. Structure and flow
3. Informativeness and relevance
4. Formatting and presentation
5. Alignment with the document intention and interpreted document intent
6. Addressing the specified focus area: {focusArea}

Please offer specific examples and concrete revisions where applicable. The suggestions should be actionable and aimed at elevating the overall quality of the document and ensuring it meets the user's requirements.
`);

const improvementPrompt = PromptTemplate.fromTemplate(`
Document Intention: {documentIntention}
Document Intent Interpretation: {documentIntent}
Focus Area: {focusArea}

Here is the original document:

{document}

And here are the suggestions for improvement:

{suggestions}

Please revise the document, incorporating the provided suggestions while maintaining the original topic and purpose. Focus on enhancing the clarity, structure, informativeness, formatting, alignment with the document intention and interpreted document intent, and addressing the specified focus area.

Implement the suggestions directly into the document, making the necessary changes and refinements. The goal is to elevate the quality of the document based on the analysis and feedback provided and ensure it meets the user's requirements.

Please present the revised document, showcasing the improvements made.
`);

const intentCheckPrompt = PromptTemplate.fromTemplate(`
Document Intention: {documentIntention}
Document Intent Interpretation: {documentIntent}
Focus Area: {focusArea}

Here is the latest version of the document:

{document}

Please answer the following questions:

1. Does this new document match the document intent?
2. Is it fully expressing the nature of what was asked for in the document intention?
3. Does it adequately address the specified focus area?
4. Is there more room for improvement and better alignment with the document intent and focus area?

Provide detailed feedback on each question and suggest specific improvements if necessary.
`);

const discrepancyCheckPrompt = PromptTemplate.fromTemplate(`
Original example document:
{exampleDocument}

Generated document:
{generatedDocument}

Focus Area: {focusArea}

Please analyze the two documents above and answer the following questions:

1. Are there any major discrepancies between the original example document and the generated document?
2. If there are discrepancies, what are they?
3. How can the generated document be improved to better align with the original example document?
4. Does the generated document adequately address the specified focus area?

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

async function interpretUserIntent(documentIntention, focusArea) {
    const intentPrompt = PromptTemplate.fromTemplate(`
      Please interpret the user's intent from the following input and focus area:
  
      Document Intention: {documentIntention}
      Focus Area: {focusArea}
  
      Provide a concise interpretation of what the user is asking for, including:
      - The main goal or purpose of the document
      - Any specific topics or requirements
      - The document type (if specified)
      - Any constraints or additional context
      - How the focus area should be incorporated into the document and its content
  
      Your interpretation should explicitly address how the focus area affects the overall intent and desired outcome.

      Your interpretation:
    `);
  
    const prompt = await intentPrompt.format({ documentIntention, focusArea });
    return await llm.invoke(prompt);
}

async function generateDocument(documentType, topic, exampleDocument, documentIntention, documentIntent, focusArea) {
  const prompt = await documentPrompt.format({ documentType, topic, exampleDocument, documentIntention, documentIntent, focusArea });
  return await llm.invoke(prompt);
}

async function analyzeDocument(document, documentIntention, documentIntent, focusArea) {
  const prompt = await analysisPrompt.format({ document, documentIntention, documentIntent, focusArea });
  return await llm.invoke(prompt);
}

async function improveDocument(document, suggestions, documentIntention, documentIntent, focusArea) {
  const prompt = await improvementPrompt.format({ document, suggestions, documentIntention, documentIntent, focusArea });
  return await llm.invoke(prompt);
}

async function checkUserIntentAlignment(document, documentIntention, documentIntent, focusArea) {
  const prompt = await intentCheckPrompt.format({ document, documentIntention, documentIntent, focusArea });
  return await llm.invoke(prompt);
}

async function checkForDiscrepancies(exampleDocument, generatedDocument, focusArea) {
  const prompt = await discrepancyCheckPrompt.format({ exampleDocument, generatedDocument, focusArea });
  return await llm.invoke(prompt);
}

async function compareDocuments(newDocument, bestDocument, previousDocument, focusArea) {
  const comparePrompt = `
    Compare the following document versions:

    New Document:
    ${newDocument}

    Best Document:
    ${bestDocument}

    Previous Document:
    ${previousDocument}

    Focus Area: ${focusArea}

    Provide a detailed analysis of the improvements made in the new document compared to the best document and previous document. Consider factors such as clarity, structure, informativeness, formatting, alignment with the user's requirements, and how well it addresses the focus area.

    Indicate which document version is the best overall and explain why.
  `;
  const comparisonResult = await llm.invoke(comparePrompt);
  return comparisonResult.trim();
}

async function generateAggregateDocument(cleanBestDocument, cleanInitialDocument, goodEnoughDocument) {
    const aggregatePrompt = `
        Compare and analyze the following document versions:

        Clean Best Document:
        ${cleanBestDocument}

        Clean Initial Document:
        ${cleanInitialDocument}

        Good Enough Document:
        ${goodEnoughDocument}

        Based on these document versions, generate a final, optimized version that combines the best aspects of each. 
        Consider clarity, structure, informativeness, formatting, and overall document quality.
        Provide a brief explanation of the choices made in creating this aggregate version.

        Aggregate Document:
    `;

    const aggregateResult = await llm.invoke(aggregatePrompt);
    return aggregateResult.trim();
}

// Chunk 4: Document Evaluation and Cleaning Functions
async function evaluateDocumentFitness(document, documentIntention, documentIntent, focusArea, iterationDir) {
    const evaluationPrompt = `
      Given the following document:
      ${document}
  
      And the document intention:
      ${documentIntention}
  
      And the interpreted document intent:
      ${documentIntent}
  
      And the focus area:
      ${focusArea}
  
      Please evaluate if the document meets the user's requirements and aligns with their intent. Consider the following criteria:
      - Content: Does the document fulfill the desired content based on the document intention?
      - Clarity: Is the document clear and easy to understand?
      - Structure: Is the document well-structured and organized?
      - Informativeness: Does the document effectively convey the necessary information?
      - Formatting: Is the document well-formatted with appropriate headings and sections?
      - Alignment: Is the document consistent with the interpreted document intent?
      - Focus Area: Does the document adequately address the specified focus area?
  
      Provide a detailed analysis of the document's fitness and indicate whether it successfully meets the user's requirements and intent. Explain your reasoning.
    `;
    const evaluationResult = await llm.invoke(evaluationPrompt);
    
    const fitnessPath = path.join(iterationDir, 'fitness_evaluation.txt');
    await fs.writeFile(fitnessPath, evaluationResult, 'utf8');
    
    const meetsRequirements = evaluationResult.toLowerCase().includes('meets the user\'s requirements');
    return meetsRequirements;
}

async function cleanDocument(document) {
    const cleanPrompt = `
      Here is a document that needs to be cleaned and formatted correctly:
  
      ${document}
  
      Please correct any grammatical errors, fix formatting issues, and ensure the document follows best practices for structure and presentation. Return only the cleaned and formatted document. Do not return any additional text or comments. Return ONLY the document and nothing else.
    `;
    const cleanedDocument = await llm.invoke(cleanPrompt);
    return cleanedDocument.trim();
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

async function saveExampleDocument(document, filePath) {
    await fs.writeFile(filePath, document, 'utf8');
    console.log(`Example document saved to ${filePath}`);
}

async function saveAutoDocument(document) {
    const autoDocumentPath = path.join(process.cwd(), 'auto_document.txt');
    const cleanedDocument = await cleanDocument(document);
    await fs.writeFile(autoDocumentPath, cleanedDocument, 'utf8');
    console.log(`Auto document saved to: ${autoDocumentPath}`);
}

async function loadConfig(configPath) {
    const config = JSON.parse(await fs.readFile(configPath, 'utf8'));
    return config;
}

async function saveConfig(configPath, config) {
    await fs.writeFile(configPath, JSON.stringify(config, null, 2), 'utf8');
    console.log(`Config saved to ${configPath}`);
}

// Chunk 6: Main Document Improvement Function
async function runDocumentImprovement(documentType, topic, exampleDocumentPath, documentIntention, documentIntent, iterations, runDir, focusArea) {
    const receipt = {
      documentType,
      topic,
      documentIntention,
      documentIntent,
      focusArea,
      iterations,
      startTime: new Date(),
      endTime: null,
      duration: null,
      initialDocumentPath: '',
      bestDocumentPath: '',
      goodEnoughDocumentPath: '',
      iterationDetails: [],
      documentIds: {
        initialDocument: '',
        bestDocument: '',
        goodEnoughDocument: '',
      },
    };
  
    console.log(`\n--- Document Improvement Process ---`);
    console.log(`Document Type: ${documentType}`);
    console.log(`Topic: ${topic}`);
    console.log(`Document Intention: ${documentIntention}`);
    console.log(`Focus Area: ${focusArea}`);
    console.log(`Number of Iterations: ${iterations}`);
    console.log(`Run Directory: ${runDir}`);
    console.log(`Start Time: ${receipt.startTime.toLocaleString()}`);
    console.log(`----------------------------------`);
  
    const exampleDocument = await fs.readFile(exampleDocumentPath, 'utf8');
    console.log(`Example document read from ${exampleDocumentPath}`);
  
    const documentIntentionPath = path.join(runDir, 'document_intention.txt');
    await saveToFile(documentIntention, documentIntentionPath);
  
    const documentIntentPath = path.join(runDir, 'document_intent.txt');
    await saveToFile(documentIntent, documentIntentPath);
  
    let initialDocument = await generateDocument(documentType, topic, exampleDocument, documentIntention, documentIntent, focusArea);
    const initialDocumentPath = path.join(runDir, 'initial_document.txt');
    receipt.documentIds.initialDocument = await saveToFile(initialDocument, initialDocumentPath);
    receipt.initialDocumentPath = initialDocumentPath;
  
    console.log(`\nInitial Document:`);
    console.log(`--------------`);
    console.log(initialDocument);
    console.log(`Saved to: ${initialDocumentPath}`);
  
    let bestDocument = initialDocument;
    let previousDocument = initialDocument;
    let goodEnoughDocument = null;
    let improvedDocument = initialDocument;

    for (let i = 1; i <= iterations; i++) {
        console.log(`\n--- Iteration ${i} ---`);
        const startTime = performance.now();

        const iterationDir = await createIterationFolder(runDir, i);
        let improvedDocumentFilePath = path.join(iterationDir, 'improved_document.txt');
        let suggestionsPath = '';
        let iterationAnalysisPath = '';
        let discrepancyCheckPath = '';

        const meetsRequirements = await evaluateDocumentFitness(improvedDocument, documentIntention, documentIntent, focusArea, iterationDir);
        console.log(`\nDocument Fitness Evaluation: ${meetsRequirements ? 'Pass' : 'Fail'}`);
  
        if (meetsRequirements && !goodEnoughDocument) {
            goodEnoughDocument = improvedDocument;
            const goodEnoughDocumentPath = path.join(runDir, 'good_enough_document.txt');
            await saveToFile(goodEnoughDocument, goodEnoughDocumentPath);
            receipt.goodEnoughDocumentPath = goodEnoughDocumentPath;
            console.log(`\nGood Enough Document saved to: ${goodEnoughDocumentPath}`);
        }
  
        console.log(`\nChecking User Intent Alignment...`);
        const intentCheckResult = await checkUserIntentAlignment(improvedDocument, documentIntention, documentIntent, focusArea);
        console.log(`\nUser Intent Alignment Check:`);
        console.log(intentCheckResult);
  
        const suggestions = await analyzeDocument(improvedDocument, documentIntention, documentIntent, focusArea);
        suggestionsPath = path.join(iterationDir, 'suggestions.txt');
        await saveToFile(suggestions, suggestionsPath);
  
        const discrepancyCheck = await checkForDiscrepancies(exampleDocument, improvedDocument, focusArea);
        discrepancyCheckPath = path.join(iterationDir, 'discrepancy_check.txt');
        await saveToFile(discrepancyCheck, discrepancyCheckPath);
  
        improvedDocument = await improveDocument(improvedDocument, suggestions + '\n' + discrepancyCheck, documentIntention, documentIntent, focusArea);
        await saveToFile(improvedDocument, improvedDocumentFilePath);

        console.log(`\nImproved Document:`);
        console.log(`--------------`);
        console.log(improvedDocument);
        console.log(`Saved to: ${improvedDocumentFilePath}`);

        const iterationAnalysis = await compareDocuments(improvedDocument, bestDocument, previousDocument, focusArea);
        iterationAnalysisPath = path.join(iterationDir, 'iteration_analysis.txt');
        await saveToFile(iterationAnalysis, iterationAnalysisPath);

        console.log(`\nIteration Analysis:`);
        console.log(`-------------------`);
        console.log(iterationAnalysis);
        console.log(`Saved to: ${iterationAnalysisPath}`);

        bestDocument = improvedDocument;

        const cleanedImprovedDocument = await cleanDocument(improvedDocument);
        const cleanedImprovedDocumentPath = path.join(iterationDir, 'cleaned_improved_document.txt');
        
        console.log(`\nCleaned Improved Document:`);
        console.log(`----------------------`);
        console.log(cleanedImprovedDocument);
        console.log(`Saved to: ${cleanedImprovedDocumentPath}`);

        // Generate and save the aggregate document after each iteration
        const aggregateDocument = await generateAggregateDocument(cleanedImprovedDocument, await cleanDocument(initialDocument), goodEnoughDocument || cleanedImprovedDocument);
        const aggregateDocumentPath = path.join(iterationDir, 'aggregate_document.txt');
        await saveToFile(aggregateDocument, aggregateDocumentPath);

        console.log(`\nAggregate Document generated and saved to: ${aggregateDocumentPath}`);

        // Save the cleaned aggregate document as auto_document.txt
        await saveAutoDocument(aggregateDocument);

        const endTime = performance.now();
        const duration = (endTime - startTime) / 1000;

        console.log(`\nIteration Duration: ${duration.toFixed(2)} seconds`);

        const iterationDetail = {
            iteration: i,
            improvedDocumentPath: improvedDocumentFilePath,
            cleanedImprovedDocumentPath,
            suggestionsPath,
            iterationAnalysisPath,
            aggregateDocumentPath,
            duration,
            documentIds: {
                improvedDocument: await saveToFile(improvedDocument, improvedDocumentFilePath),
                cleanedImprovedDocument: await saveToFile(cleanedImprovedDocument, cleanedImprovedDocumentPath),
                suggestions: suggestionsPath ? await saveToFile(suggestions, suggestionsPath) : '',
                iterationAnalysis: iterationAnalysisPath ? await saveToFile(iterationAnalysis, iterationAnalysisPath) : '',
                discrepancyCheck: discrepancyCheckPath ? await saveToFile(discrepancyCheck, discrepancyCheckPath) : '',
                aggregateDocument: await saveToFile(aggregateDocument, aggregateDocumentPath),
            },
        };

        receipt.iterationDetails.push(iterationDetail);
        previousDocument = improvedDocument;
    }

    const bestDocumentPath = path.join(runDir, 'best_document.txt');
    await saveToFile(bestDocument, bestDocumentPath);
    receipt.bestDocumentPath = bestDocumentPath;

    console.log(`\nBest Document (Final Iteration):`);
    console.log(`-----------------------------`);
    console.log(bestDocument);
    console.log(`Saved to: ${bestDocumentPath}`);

    const cleanBestDocument = await cleanDocument(bestDocument);
    const cleanBestDocumentPath = path.join(runDir, 'clean_best_document.txt');
    await saveToFile(cleanBestDocument, cleanBestDocumentPath);

    const cleanInitialDocument = await cleanDocument(initialDocument);
    const cleanInitialDocumentPath = path.join(runDir, 'clean_initial_document.txt');
    await saveToFile(cleanInitialDocument, cleanInitialDocumentPath);

    // Generate final aggregate document
    const finalAggregateDocument = await generateAggregateDocument(cleanBestDocument, cleanInitialDocument, goodEnoughDocument || cleanBestDocument);
    const finalAggregateDocumentPath = path.join(runDir, 'final_aggregate_document.txt');
    await saveToFile(finalAggregateDocument, finalAggregateDocumentPath);

    console.log(`\nFinal Aggregate Document generated and saved to: ${finalAggregateDocumentPath}`);

    // Save the final cleaned aggregate document as auto_document.txt
    await saveAutoDocument(finalAggregateDocument);

    receipt.endTime = new Date();
    receipt.duration = (receipt.endTime - receipt.startTime) / 1000;

    console.log(`\n--- Document Improvement Process Completed ---`);
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

    const newExampleDocumentPath = path.join(process.cwd(), 'example_document.txt');
    await saveToFile(cleanBestDocument, newExampleDocumentPath);

    return receipt;
}

// Chunk 7: Receipt Generation and Focus Area Functions
function generateReceiptContent(receipt) {
    let content = `Document Improvement Run Receipt\n`;
    content += `===========================\n\n`;
    content += `**Document Type:** ${receipt.documentType}\n`;
    content += `**Topic:** ${receipt.topic}\n`;
    content += `**Document Intention:** ${receipt.documentIntention}\n`;
    content += `**Focus Area:** ${receipt.focusArea}\n`;
    content += `**Number of Iterations:** ${receipt.iterations}\n`;
    content += `**Start Time:** ${receipt.startTime.toLocaleString()}\n`;
    content += `**End Time:** ${receipt.endTime.toLocaleString()}\n`;
    content += `**Total Duration:** ${receipt.duration.toFixed(2)} seconds\n\n`;
    content += `**Initial Document:** ${receipt.initialDocumentPath} (ID: ${receipt.documentIds.initialDocument})\n`;
    content += `**Best Document:** ${receipt.bestDocumentPath} (ID: ${receipt.documentIds.bestDocument})\n`;
    content += `**Good Enough Document:** ${receipt.goodEnoughDocumentPath} (ID: ${receipt.documentIds.goodEnoughDocument})\n\n`;
    content += `## Iteration Details:\n`;

    for (const detail of receipt.iterationDetails) {
        content += `### Iteration ${detail.iteration}:\n`;
        content += `- **Improved Document:** ${detail.improvedDocumentPath} (ID: ${detail.documentIds.improvedDocument})\n`;
        content += `- **Cleaned Improved Document:** ${detail.cleanedImprovedDocumentPath} (ID: ${detail.documentIds.cleanedImprovedDocument})\n`;
        content += `- **Suggestions:** ${detail.suggestionsPath} (ID: ${detail.documentIds.suggestions})\n`;
        if (detail.documentIds.discrepancyCheck) {
            content += `- **Discrepancy Check:** ${detail.discrepancyCheckPath} (ID: ${detail.documentIds.discrepancyCheck})\n`;
        }
        content += `- **Iteration Analysis:** ${detail.iterationAnalysisPath} (ID: ${detail.documentIds.iterationAnalysis})\n`;
        content += `- **Aggregate Document:** ${detail.aggregateDocumentPath} (ID: ${detail.documentIds.aggregateDocument})\n`;
        content += `- **Duration:** ${detail.duration.toFixed(2)} seconds\n\n`;
    }

    return content;
}

async function generateFocusArea(documentIntention, previousFocusArea, nextSteps) {
    const focusAreaPrompt = PromptTemplate.fromTemplate(`
      Based on the following information:

      Document Intention: {documentIntention}
      Previous Focus Area: {previousFocusArea}
      Next Steps: {nextSteps}

      Generate a new focus area for the next round of document improvement. The focus area should address the most critical aspects mentioned in the next steps while considering the overall document intention.

      New Focus Area:
    `);

    const prompt = await focusAreaPrompt.format({ documentIntention, previousFocusArea, nextSteps });
    return await llm.invoke(prompt);
}

async function evaluateNextSteps(bestDocument, documentIntention, focusArea) {
    const nextStepsPrompt = PromptTemplate.fromTemplate(`
      Analyze the following document and provide next steps for further improvement:

      Document:
      {bestDocument}

      Document Intention: {documentIntention}
      Current Focus Area: {focusArea}

      Evaluate the document and suggest specific next steps for improvement. Consider the following aspects:
      1. Content quality and relevance
      2. Structure and organization
      3. Clarity and readability
      4. Alignment with the document intention
      5. Areas that weren't fully addressed in the current focus area

      If you believe the document has reached a satisfactory state and no further improvements are necessary, explicitly state that there are no more next steps.

      Next Steps:
    `);

    const prompt = await nextStepsPrompt.format({ bestDocument, documentIntention, focusArea });
    return await llm.invoke(prompt);
}

// Chunk 8: Main Function
async function main() {
    const configPath = path.join(process.cwd(), 'config.json');
    let config = await loadConfig(configPath);
    let { documentType, topic, exampleDocumentPath, iterations, documentIntention, focusArea, nextSteps } = config;

    if (!focusArea) {
        focusArea = "Initial focus on document structure and content organization";
    }
    if (!nextSteps) {
        nextSteps = "Begin by outlining main points and developing a coherent narrative.";
    }

    while (true) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const runName = `run_${timestamp}`;
        const runDir = path.join(process.cwd(), 'document-iterations', runName);
        await fs.mkdir(runDir, { recursive: true });

        console.log(`\nStarting new iteration with focus area: ${focusArea}`);
        console.log(`Next steps from previous iteration: ${nextSteps}`);

        const documentIntent = await interpretUserIntent(documentIntention, focusArea);
        if (documentIntent) {
            const documentIntentPath = path.join(runDir, 'document_intent.txt');
            await saveToFile(documentIntent, documentIntentPath);
            console.log("Document intent interpreted and saved.");
        } else {
            console.warn("Warning: Failed to interpret document intent. Proceeding without it.");
        }

        const receipt = await runDocumentImprovement(documentType, topic, exampleDocumentPath, documentIntention, documentIntent, iterations, runDir, focusArea);

        await saveExampleDocument(await fs.readFile(receipt.bestDocumentPath, 'utf8'), exampleDocumentPath);

        const bestDocument = await fs.readFile(receipt.bestDocumentPath, 'utf8');
        nextSteps = await evaluateNextSteps(bestDocument, documentIntention, focusArea);
        const nextStepsPath = path.join(runDir, 'next_steps.txt');
        await saveToFile(nextSteps, nextStepsPath);

        console.log("\nNext steps:");
        console.log(nextSteps);

        if (nextSteps.toLowerCase().includes("no more next steps") || nextSteps.trim() === "") {
            console.log("No more improvements needed. Stopping the process.");
            break;
        }

        focusArea = await generateFocusArea(documentIntention, focusArea, nextSteps);
        console.log(`\nNew focus area for next iteration: ${focusArea}`);

        config.focusArea = focusArea;
        config.nextSteps = nextSteps;
        config.lastAggregateDocumentPath = path.join(runDir, 'final_aggregate_document.txt');
        await saveConfig(configPath, config);
        console.log("Config updated with new focus area, next steps, and last aggregate document path.");

        await new Promise(resolve => setTimeout(resolve, 5000));
    }

    console.log("Automated document improvement process completed.");
}

main();
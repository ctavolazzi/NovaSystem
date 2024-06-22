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
<!--
  ModelSelector.svelte - Component for selecting LLM models
  This component provides a dropdown for selecting different LLM models.
-->
<script lang="ts">
  import { onMount } from 'svelte';
  import api from '$lib/api';
  import type { OllamaModel } from '$lib/api';

  // Props
  export let selectedModel: string = 'llama3';
  export let isLocal: boolean = true;

  // Local state
  let availableModels: Array<{name: string, size: string, description: string}> = [];
  let isLoading = false;
  let error: string | null = null;
  let ollamaStatus: 'running' | 'not_running' | 'checking' = 'checking';

  // Fetch available models when mounted
  onMount(async () => {
    await checkOllamaStatus();
    if (isLocal && ollamaStatus === 'running') {
      await fetchOllamaModels();
    } else if (isLocal) {
      // Default to non-local if Ollama is not running
      isLocal = false;
      setCloudModels();
    } else {
      setCloudModels();
    }
  });

  // Check if Ollama is running
  async function checkOllamaStatus() {
    try {
      const status = await api.getOllamaStatus();
      ollamaStatus = status.status;
      return status.status === 'running';
    } catch (err) {
      console.error('Error checking Ollama status:', err);
      ollamaStatus = 'not_running';
      return false;
    }
  }

  // Fetch available Ollama models
  async function fetchOllamaModels() {
    isLoading = true;
    error = null;

    try {
      // Fetch real models from the Ollama API
      const ollamaModels = await api.listOllamaModels();

      // Map to the format our component uses
      availableModels = ollamaModels.map(model => {
        const size = model.details?.parameter_size || '';
        let description = 'Ollama model';

        // Generate description based on model name
        if (model.name.includes('llama3')) {
          description = 'General purpose model';
        } else if (model.name.includes('mistral')) {
          description = 'Strong reasoning capabilities';
        } else if (model.name.includes('gemma')) {
          description = 'Google\'s well-rounded model';
        } else if (model.name.includes('codellama')) {
          description = 'Specialized for code generation';
        } else if (model.name.includes('phi')) {
          description = 'Microsoft\'s compact model';
        }

        return {
          name: model.name,
          size: size,
          description: description
        };
      });

      // If no models available, show error
      if (availableModels.length === 0) {
        error = 'No models found in Ollama. Please pull a model first.';
        // Fallback to minimal list
        availableModels = [
          { name: 'llama3', size: '8B', description: 'Default model (not installed)' }
        ];
      }

      // Use the first model as default if none selected
      if (!selectedModel && availableModels.length > 0) {
        selectedModel = availableModels[0].name;
      }
    } catch (err) {
      console.error('Error fetching Ollama models:', err);
      error = 'Failed to fetch available models. Using default options.';

      // Fallback to minimal list
      availableModels = [
        { name: 'llama3', size: '8B', description: 'Default model' }
      ];
    } finally {
      isLoading = false;
    }
  }

  // Set cloud LLM provider models
  function setCloudModels() {
    availableModels = [
      { name: 'gpt-4', size: '', description: 'Most capable OpenAI model' },
      { name: 'gpt-3.5-turbo', size: '', description: 'Faster, more economical' }
    ];
    selectedModel = 'gpt-3.5-turbo';
  }

  // Toggle between local and cloud models
  async function toggleModelSource() {
    isLocal = !isLocal;

    if (isLocal) {
      // Check if Ollama is running before trying to fetch models
      const isRunning = await checkOllamaStatus();
      if (isRunning) {
        await fetchOllamaModels();
      } else {
        error = 'Ollama is not running. Unable to use local models.';
        isLocal = false; // Revert back to cloud
        setCloudModels();
      }
    } else {
      setCloudModels();
    }
  }
</script>

<div class="model-selector">
  <div class="mb-4">
    <label class="flex items-center space-x-2 text-sm font-medium text-gray-700">
      <input
        type="checkbox"
        bind:checked={isLocal}
        on:change={toggleModelSource}
        class="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
      <span>Use local models (Ollama)</span>

      <!-- Status indicator -->
      {#if ollamaStatus === 'checking'}
        <span class="ml-2 inline-block w-3 h-3 bg-yellow-400 rounded-full"></span>
      {:else if ollamaStatus === 'running'}
        <span class="ml-2 inline-block w-3 h-3 bg-green-500 rounded-full"></span>
      {:else}
        <span class="ml-2 inline-block w-3 h-3 bg-red-500 rounded-full"
          title="Ollama is not running"></span>
      {/if}
    </label>

    {#if ollamaStatus === 'not_running' && isLocal}
      <div class="mt-1 text-xs text-red-500">
        Ollama is not running. Start Ollama or switch to cloud models.
      </div>
    {/if}
  </div>

  <div class="mb-3">
    <label for="model-select" class="block text-sm font-medium text-gray-700 mb-1">
      {isLocal ? 'Select Ollama Model' : 'Select Cloud Model'}
    </label>

    {#if isLoading}
      <div class="text-sm text-gray-500">Loading available models...</div>
    {:else if error}
      <div class="text-sm text-red-500 mb-2">{error}</div>
    {/if}

    <select
      id="model-select"
      bind:value={selectedModel}
      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
      {#each availableModels as model}
        <option value={model.name}>
          {model.name} {model.size ? `(${model.size})` : ''} - {model.description}
        </option>
      {/each}
    </select>

    {#if isLocal}
      <p class="mt-1 text-xs text-gray-500">
        Models run locally on your computer using Ollama.
        <a href="/docs/guides/using_ollama" class="text-blue-500 hover:underline">Learn more</a>
      </p>
    {:else}
      <p class="mt-1 text-xs text-gray-500">
        Cloud models require API keys configured in the backend.
      </p>
    {/if}
  </div>
</div>

<style>
  /* Add any custom styles here */
</style>
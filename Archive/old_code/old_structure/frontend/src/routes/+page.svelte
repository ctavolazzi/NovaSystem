<!--
  Main page for NovaSystem
  This page displays a list of available agents and allows the user to interact with them.
-->
<script lang="ts">
  import { onMount } from 'svelte';
  import api from '$lib/api';
  import type { Agent } from '$lib/api';
  import Chat from '../components/Chat.svelte';
  import ModelSelector from '../components/ModelSelector.svelte';

  // State
  let agents: Agent[] = [];
  let selectedAgent: Agent | null = null;
  let isLoading = true;
  let error: string | null = null;

  // Form state for creating a new agent
  let showCreateForm = false;
  let newAgentName = '';
  let newAgentType = 'dce';
  let isCreatingAgent = false;
  let selectedModel = 'llama3';
  let useLocalModels = true;

  onMount(async () => {
    await loadAgents();
  });

  // Load the list of agents
  async function loadAgents() {
    isLoading = true;
    error = null;

    try {
      // Check if the API is healthy
      const isHealthy = await api.healthCheck();
      if (!isHealthy) {
        error = 'The NovaSystem API is not available. Please make sure the backend is running.';
        return;
      }

      // Get the list of agents
      agents = await api.listAgents();

      // Select the first agent if available and none selected
      if (agents.length > 0 && !selectedAgent) {
        selectedAgent = agents[0];
      }
    } catch (err) {
      console.error('Error loading agents:', err);
      error = 'Failed to load agents. Please check if the backend is running.';
    } finally {
      isLoading = false;
    }
  }

  // Create a new agent
  async function createAgent() {
    if (!newAgentName.trim()) {
      error = 'Please enter a name for the agent.';
      return;
    }

    isCreatingAgent = true;
    error = null;

    try {
      // Prepare agent configuration with model settings
      const agentConfig = {
        provider_config: {
          default_model: selectedModel
        }
      };

      // For cloud models, we need to set the provider class
      if (!useLocalModels) {
        agentConfig.provider_class = 'OpenAIProvider';
      }

      // Create the agent
      const newAgent = await api.createAgent({
        agent_type: newAgentType,
        name: newAgentName.trim(),
        config: agentConfig
      });

      // Add the new agent to the list
      agents = [...agents, newAgent];

      // Select the new agent
      selectedAgent = newAgent;

      // Reset the form
      newAgentName = '';
      showCreateForm = false;
    } catch (err) {
      console.error('Error creating agent:', err);
      error = 'Failed to create agent. Please try again.';
    } finally {
      isCreatingAgent = false;
    }
  }

  // Delete an agent
  async function deleteAgent(agent: Agent) {
    if (!confirm(`Are you sure you want to delete ${agent.name}?`)) {
      return;
    }

    try {
      await api.deleteAgent(agent.id);

      // Remove the agent from the list
      agents = agents.filter(a => a.id !== agent.id);

      // If the deleted agent was selected, select another one
      if (selectedAgent && selectedAgent.id === agent.id) {
        selectedAgent = agents.length > 0 ? agents[0] : null;
      }
    } catch (err) {
      console.error('Error deleting agent:', err);
      error = 'Failed to delete agent. Please try again.';
    }
  }
</script>

<div class="min-h-screen bg-gray-100">
  <header class="bg-gray-900 text-white p-6">
    <div class="container mx-auto">
      <h1 class="text-3xl font-bold">NovaSystem</h1>
      <p class="text-gray-300">Multi-Agent Problem Solving Framework</p>
    </div>
  </header>

  <main class="container mx-auto py-6 px-4">
    {#if error}
      <div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6" role="alert">
        <p>{error}</p>
      </div>
    {/if}

    <div class="flex flex-col md:flex-row gap-6">
      <!-- Sidebar -->
      <div class="w-full md:w-64 bg-white rounded-lg shadow-md p-4">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">Agents</h2>
          <button
            class="text-blue-600 hover:text-blue-800"
            on:click={() => showCreateForm = !showCreateForm}>
            {showCreateForm ? 'Cancel' : 'Add Agent'}
          </button>
        </div>

        {#if showCreateForm}
          <div class="mb-4 p-3 bg-gray-50 rounded-md">
            <h3 class="text-lg font-medium mb-2">Create New Agent</h3>
            <form on:submit|preventDefault={createAgent}>
              <div class="mb-3">
                <label for="agent-type" class="block text-sm font-medium text-gray-700">Type</label>
                <select
                  id="agent-type"
                  bind:value={newAgentType}
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                  <option value="dce">Discussion Continuity Expert (DCE)</option>
                  <!-- Add more agent types as they become available -->
                </select>
              </div>

              <div class="mb-3">
                <label for="agent-name" class="block text-sm font-medium text-gray-700">Name</label>
                <input
                  id="agent-name"
                  type="text"
                  bind:value={newAgentName}
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  placeholder="Enter agent name" />
              </div>

              <!-- Model Selector Component -->
              <div class="mb-3">
                <ModelSelector
                  bind:selectedModel={selectedModel}
                  bind:isLocal={useLocalModels} />
              </div>

              <button
                type="submit"
                disabled={isCreatingAgent || !newAgentName.trim()}
                class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
                {isCreatingAgent ? 'Creating...' : 'Create Agent'}
              </button>
            </form>
          </div>
        {/if}

        {#if isLoading}
          <div class="py-4 text-center text-gray-500">
            Loading agents...
          </div>
        {:else if agents.length === 0}
          <div class="py-4 text-center text-gray-500">
            No agents available. Create one to get started.
          </div>
        {:else}
          <ul class="space-y-2">
            {#each agents as agent (agent.id)}
              <li class="flex justify-between items-center rounded-md p-2 {selectedAgent?.id === agent.id ? 'bg-blue-50' : 'hover:bg-gray-50'}">
                <button
                  class="flex-1 text-left"
                  on:click={() => selectedAgent = agent}>
                  <div class="font-medium">{agent.name}</div>
                  <div class="text-sm text-gray-500">{agent.role}</div>
                </button>
                <button
                  class="text-red-500 hover:text-red-700 ml-2"
                  on:click={() => deleteAgent(agent)}>
                  Delete
                </button>
              </li>
            {/each}
          </ul>
        {/if}

        <div class="mt-6 pt-4 border-t border-gray-200">
          <button
            class="w-full bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300"
            on:click={loadAgents}>
            Refresh Agents
          </button>
        </div>
      </div>

      <!-- Main content area -->
      <div class="flex-1">
        {#if selectedAgent}
          <div class="bg-white rounded-lg shadow-md h-[600px]">
            <Chat agent={selectedAgent} />
          </div>
        {:else}
          <div class="bg-white rounded-lg shadow-md p-8 text-center">
            <h2 class="text-xl font-semibold mb-4">Welcome to NovaSystem</h2>
            <p class="mb-4">Select an agent from the sidebar or create a new one to start a conversation.</p>

            {#if agents.length === 0 && !isLoading}
              <button
                class="mt-4 bg-blue-600 text-white py-2 px-6 rounded-md hover:bg-blue-700"
                on:click={() => showCreateForm = true}>
                Create Your First Agent
              </button>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </main>

  <footer class="bg-gray-800 text-white py-6 mt-12">
    <div class="container mx-auto px-4 text-center">
      <p>&copy; {new Date().getFullYear()} NovaSystem Project</p>
    </div>
  </footer>
</div>

<style>
  /* Add custom styles here */
</style>
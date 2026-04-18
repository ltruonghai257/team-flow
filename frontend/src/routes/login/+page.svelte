<script lang="ts">
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { Eye, EyeOff } from 'lucide-svelte';

	let username = '';
	let password = '';
	let showPassword = false;
	let loading = false;

	async function handleLogin() {
		if (!username || !password) return;
		loading = true;
		try {
			await authStore.login(username, password);
			goto('/');
		} catch (e) {
			toast.error(e.message || 'Login failed');
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head><title>Login · TeamFlow</title></svelte:head>

<div class="min-h-screen bg-gray-950 flex items-center justify-center p-4">
	<div class="w-full max-w-sm">
		<div class="text-center mb-8">
			<div class="w-12 h-12 bg-primary-600 rounded-xl flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">T</div>
			<h1 class="text-2xl font-bold text-white">Welcome back</h1>
			<p class="text-gray-400 mt-1 text-sm">Sign in to TeamFlow</p>
		</div>

		<form on:submit|preventDefault={handleLogin} class="card space-y-4">
			<div>
				<label class="label" for="username">Username</label>
				<input id="username" bind:value={username} type="text" class="input" placeholder="your_username" autocomplete="username" required />
			</div>
			<div>
				<label class="label" for="password">Password</label>
				<div class="relative">
					{#if showPassword}
						<input id="password" bind:value={password} type="text" class="input pr-10" placeholder="••••••••" autocomplete="current-password" required />
					{:else}
						<input id="password" bind:value={password} type="password" class="input pr-10" placeholder="••••••••" autocomplete="current-password" required />
					{/if}
					<button type="button" on:click={() => (showPassword = !showPassword)} class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">
						{#if showPassword}<EyeOff size={16} />{:else}<Eye size={16} />{/if}
					</button>
				</div>
			</div>
			<button type="submit" class="btn-primary w-full justify-center" disabled={loading}>
				{#if loading}
					<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
				{/if}
				Sign In
			</button>
		</form>

		<p class="text-center text-sm text-gray-500 mt-4">
			Don't have an account?
			<a href="/register" class="text-primary-400 hover:text-primary-300">Register</a>
		</p>
	</div>
</div>
